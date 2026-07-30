# Academy: Autenticação Multi-Tenant com JWT

Esta aula registra a fundação técnica criada na DEV-005.

## Ideias principais

- O tenant deve ser resolvido pelo backend.
- Access token identifica usuário, tenant e tipo de token.
- Refresh token deve ser opaco e armazenado apenas como hash.
- Rotação reduz o impacto de vazamento de refresh token.
- Logout é revogação de sessão.

## Fluxo

1. Usuário envia tenant, email e senha.
2. Backend resolve tenant.
3. Backend valida senha.
4. Backend emite access token e refresh token.
5. Frontend salva tokens em storage seguro.
6. Requests protegidas usam Bearer token.
7. Refresh renova a sessão e invalida o refresh anterior.

Nenhuma regra de negócio do ERP faz parte desta aula.
