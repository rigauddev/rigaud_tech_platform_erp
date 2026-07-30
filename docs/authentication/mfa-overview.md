# Autenticação em Dois Fatores

DEV-009 adiciona MFA ao módulo Auth sem alterar a arquitetura definida.

Canais:

- Aplicativo autenticador com TOTP, recomendado.
- Email com OTP temporário.
- SMS com OTP temporário e provider isolado.
- Recovery codes para emergência.

O login com usuário sem MFA continua emitindo tokens normalmente. O login com MFA ativo retorna `AUTH_MFA_REQUIRED` e só emite access/refresh token após `/api/v1/auth/mfa/verify`.
