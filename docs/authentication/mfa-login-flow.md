# Fluxo de Login MFA

1. Cliente envia tenant, email e senha.
2. Backend valida credenciais.
3. Sem MFA ativo, emite tokens.
4. Com MFA ativo, cria challenge temporário e retorna `AUTH_MFA_REQUIRED`.
5. Cliente envia `challenge_id`, método e código.
6. Backend valida o segundo fator, consome o challenge e emite tokens.

Senha, OTP, TOTP, recovery code e segredo TOTP não são armazenados no Flutter.
