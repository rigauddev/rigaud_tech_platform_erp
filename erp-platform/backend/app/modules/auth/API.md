# Auth API

Endpoints técnicos da DEV-005:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/auth/mfa/status`
- `POST /api/v1/auth/mfa/totp/setup`
- `POST /api/v1/auth/mfa/totp/confirm`
- `POST /api/v1/auth/mfa/email/setup`
- `POST /api/v1/auth/mfa/email/confirm`
- `POST /api/v1/auth/mfa/sms/setup`
- `POST /api/v1/auth/mfa/sms/confirm`
- `POST /api/v1/auth/mfa/verify`

Payload de login:

```json
{
  "tenant": "rigaud-demo",
  "email": "admin@example.com",
  "password": "Senha123"
}
```
