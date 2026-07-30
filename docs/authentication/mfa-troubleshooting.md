# Troubleshooting MFA

Erro de provider indisponível:

- Verifique `REDIS_URL`.
- Verifique `MFA_ENCRYPTION_KEY`.
- Verifique Mailpit/SMTP em desenvolvimento.
- Em produção, configure providers reais para email/SMS.

Erro de CodeSign no macOS/iOS:

Execute diagnóstico restrito ao workspace antes de qualquer limpeza:

```bash
xattr -lr erp-platform/frontend
find erp-platform/frontend -name '._*' -print
```
