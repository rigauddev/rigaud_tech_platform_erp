# ADR 0002: Estratégia de Autenticação Multi-Tenant

## Status

Aceita.

## Contexto

A plataforma precisa autenticar usuários em ambiente multi-tenant sem depender ainda dos módulos completos de empresas e usuários.

## Decisão

Usar login com `email` e `password`.

O backend resolve internamente `tenant_id`, filial ativa e papel a partir do usuário autenticado.

Access tokens serão JWTs curtos com `sub`, `tenant_id`, `branch_id` e `role`. Refresh tokens serão opacos, rotacionáveis e persistidos apenas como hash.

## Consequências

- O cliente não controla `tenant_id`.
- O cliente não envia tenant no login.
- O sistema já fica preparado para isolamento por tenant.
- Email autenticável passa a ser único globalmente enquanto não houver suporte ativo a usuário multiempresa.
- Reuso de refresh token revogado é detectado e auditado.
