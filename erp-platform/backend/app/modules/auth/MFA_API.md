# Auth MFA API

Endpoints:

- `GET /api/v1/auth/mfa/status`
- `POST /api/v1/auth/mfa/totp/setup`
- `POST /api/v1/auth/mfa/totp/confirm`
- `POST /api/v1/auth/mfa/email/setup`
- `POST /api/v1/auth/mfa/email/confirm`
- `POST /api/v1/auth/mfa/sms/setup`
- `POST /api/v1/auth/mfa/sms/confirm`
- `POST /api/v1/auth/mfa/methods/{method_id}/primary`
- `DELETE /api/v1/auth/mfa/methods/{method_id}`
- `POST /api/v1/auth/mfa/disable`
- `POST /api/v1/auth/mfa/recovery-codes/regenerate`
- `POST /api/v1/auth/mfa/verify`
