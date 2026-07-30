from __future__ import annotations

import json
import time
from typing import Any, ClassVar
from uuid import UUID

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.environment import Environment
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.domain.exceptions import MfaProviderUnavailableError
from app.modules.auth.domain.repositories import MfaChallengeStore


class RedisMfaChallengeStore(MfaChallengeStore):
    _memory_store: ClassVar[dict[str, tuple[float, dict[str, Any]]]] = {}

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or settings.redis_url
        self._redis = Redis.from_url(self.redis_url, decode_responses=True)

    async def create(self, payload: dict[str, Any], expires_in: int) -> str:
        challenge_id = TokenService().create_refresh_token().token
        await self.update(challenge_id, payload, expires_in)
        return challenge_id

    async def get(self, challenge_id: str) -> dict[str, Any] | None:
        try:
            value = await self._redis.get(self._key(challenge_id))
        except RedisError as exc:
            return self._memory_get(challenge_id, exc)
        if value is None:
            return None
        return json.loads(value)

    async def update(self, challenge_id: str, payload: dict[str, Any], expires_in: int) -> None:
        serialized = json.dumps(payload, default=str)
        try:
            await self._redis.set(self._key(challenge_id), serialized, ex=expires_in)
            await self._redis.sadd(self._user_key(payload["user_id"]), challenge_id)
            await self._redis.expire(self._user_key(payload["user_id"]), expires_in)
        except RedisError as exc:
            self._memory_set(challenge_id, payload, expires_in, exc)

    async def delete(self, challenge_id: str) -> None:
        try:
            await self._redis.delete(self._key(challenge_id))
        except RedisError as exc:
            if settings.app_env == Environment.PRODUCTION:
                raise MfaProviderUnavailableError("MFA challenge store unavailable.") from exc
            self._memory_store.pop(challenge_id, None)

    async def revoke_user_challenges(self, user_id: UUID) -> None:
        user_key = self._user_key(str(user_id))
        try:
            challenge_ids = await self._redis.smembers(user_key)
            if challenge_ids:
                await self._redis.delete(
                    *(self._key(challenge_id) for challenge_id in challenge_ids)
                )
            await self._redis.delete(user_key)
        except RedisError as exc:
            if settings.app_env == Environment.PRODUCTION:
                raise MfaProviderUnavailableError("MFA challenge store unavailable.") from exc
            for challenge_id, (_, payload) in list(self._memory_store.items()):
                if payload.get("user_id") == str(user_id):
                    self._memory_store.pop(challenge_id, None)

    def _memory_get(self, challenge_id: str, exc: Exception) -> dict[str, Any] | None:
        if settings.app_env == Environment.PRODUCTION:
            raise MfaProviderUnavailableError("MFA challenge store unavailable.") from exc
        record = self._memory_store.get(challenge_id)
        if record is None:
            return None
        expires_at, payload = record
        if expires_at <= time.time():
            self._memory_store.pop(challenge_id, None)
            return None
        return payload

    def _memory_set(
        self, challenge_id: str, payload: dict[str, Any], expires_in: int, exc: Exception
    ) -> None:
        if settings.app_env == Environment.PRODUCTION:
            raise MfaProviderUnavailableError("MFA challenge store unavailable.") from exc
        self._memory_store[challenge_id] = (time.time() + expires_in, payload)

    @staticmethod
    def _key(challenge_id: str) -> str:
        return f"mfa:challenge:{challenge_id}"

    @staticmethod
    def _user_key(user_id: str) -> str:
        return f"mfa:user:{user_id}:challenges"
