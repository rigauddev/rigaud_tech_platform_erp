# Auth MFA Rules

- TOTP é recomendado.
- Apenas um método ativo pode ser principal.
- Métodos pendentes ou desabilitados não autenticam.
- Recovery code é de uso único.
- Segredos e códigos não entram em logs, auditoria ou respostas públicas.
