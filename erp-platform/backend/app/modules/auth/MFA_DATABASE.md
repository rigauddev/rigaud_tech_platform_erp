# Auth MFA Database

Tabelas permanentes:

- `user_mfa_methods`
- `mfa_recovery_codes`

Challenges temporários usam Redis preferencialmente e não criam tabela permanente.
