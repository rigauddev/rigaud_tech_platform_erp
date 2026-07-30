# Auth Database

Tabelas técnicas:

- `auth_users`
- `auth_sessions`
- `user_mfa_methods`
- `mfa_recovery_codes`

`auth_users` existe apenas como entidade mínima de autenticação.

`auth_sessions` armazena somente hash de refresh token, expiração, revogação e metadados técnicos de sessão.

`user_mfa_methods` armazena configuração técnica de métodos MFA. Segredos TOTP são criptografados.

`mfa_recovery_codes` armazena apenas hashes de recovery codes.
