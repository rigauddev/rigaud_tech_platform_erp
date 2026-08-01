from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuthBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LoginRequest(AuthBaseSchema):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(AuthBaseSchema):
    refresh_token: str = Field(min_length=32, max_length=512)


class LogoutRequest(AuthBaseSchema):
    refresh_token: str = Field(min_length=32, max_length=512)


class TokenResponse(AuthBaseSchema):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class ContextAccessTokenResponse(AuthBaseSchema):
    access_token: str
    token_type: str
    expires_in: int
    active_context: dict[str, object | None]


class LogoutResponse(AuthBaseSchema):
    message: str


class CurrentUserResponse(AuthBaseSchema):
    id: UUID
    tenant_id: UUID
    email: str
    is_active: bool
    is_superuser: bool
    membership_id: UUID | None = None
    branch_id: UUID | None = None
    branch_membership_id: UUID | None = None
    role: str | None = None
    access_scope: str | None = None


class SwitchContextRequest(AuthBaseSchema):
    tenant_id: UUID
    branch_id: UUID | None = None


class MfaMethodResponse(AuthBaseSchema):
    id: UUID
    type: str
    status: str
    is_primary: bool
    destination: str | None = None
    verified_at: str | None = None
    last_used_at: str | None = None


class MfaStatusResponse(AuthBaseSchema):
    state: str
    enabled: bool
    primary_method_id: UUID | None
    methods: list[MfaMethodResponse]
    recovery_codes_remaining: int


class MfaLoginMethodResponse(AuthBaseSchema):
    id: UUID
    type: str
    destination: str | None = None


class MfaRequiredResponse(AuthBaseSchema):
    mfa_required: bool
    challenge_id: str
    available_methods: list[MfaLoginMethodResponse]
    expires_in: int


class MfaVerifyRequest(AuthBaseSchema):
    challenge_id: str = Field(min_length=32, max_length=512)
    method: str = Field(min_length=3, max_length=32)
    code: str = Field(min_length=4, max_length=32)


class MfaCodeRequest(AuthBaseSchema):
    code: str = Field(min_length=4, max_length=32)


class MfaOtpConfirmRequest(MfaCodeRequest):
    challenge_id: str = Field(min_length=32, max_length=512)


class MfaTotpSetupResponse(AuthBaseSchema):
    method_id: UUID
    secret: str
    otpauth_uri: str
    issuer: str
    expires_in: int


class MfaOtpSetupResponse(AuthBaseSchema):
    method_id: UUID
    challenge_id: str
    destination: str | None
    expires_in: int


class MfaRecoveryCodesResponse(AuthBaseSchema):
    codes: list[str]


class MfaDisableRequest(AuthBaseSchema):
    current_password: str = Field(min_length=1, max_length=128)


class MfaMessageResponse(AuthBaseSchema):
    message: str
