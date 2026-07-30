# Users Backend

Backend implementado em `erp-platform/backend/app/modules/users`.

## Camadas

- `domain`: `UserStatus`, exceptions e repository contract.
- `application`: use cases e validações.
- `infrastructure`: repository SQLAlchemy.
- `presentation`: schemas Pydantic e router FastAPI.

## Endpoints

- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `POST /api/v1/users/me/change-password`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `POST /api/v1/users/{user_id}/activate`
- `POST /api/v1/users/{user_id}/deactivate`
- `POST /api/v1/users/{user_id}/block`
- `POST /api/v1/users/{user_id}/unblock`
- `POST /api/v1/users/{user_id}/reset-password`

Swagger segue disponível em `/docs`.
