# Segurança MFA

Dados proibidos em logs e auditoria:

- segredo TOTP;
- OTP;
- recovery code;
- senha;
- token;
- URI `otpauth`;
- QR Code.

Alterações críticas de MFA revogam refresh sessions existentes. Access tokens já emitidos seguem a limitação documentada do MVP, sem blacklist global nesta task.
