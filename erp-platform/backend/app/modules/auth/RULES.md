# Auth Rules

- Não confiar em `tenant_id` enviado pelo cliente.
- Resolver tenant via slug/código técnico.
- Não armazenar refresh token em texto puro.
- Rotacionar refresh token a cada uso.
- Revogar sessão no logout.
- Retornar erro genérico para credenciais inválidas.

Nenhuma regra de negócio do ERP foi implementada.
