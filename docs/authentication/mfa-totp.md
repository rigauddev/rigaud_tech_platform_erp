# MFA TOTP

TOTP usa biblioteca confiável (`pyotp`) e segredo criptografado com Fernet.

O endpoint `/api/v1/auth/mfa/totp/setup` retorna o segredo somente durante o enrollment, junto da URI `otpauth`.

O Flutter gera QR Code localmente a partir da URI. Após confirmação, o segredo não deve ser mantido em memória além do necessário.
