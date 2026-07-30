# ADR 0002: Estratégia de Autenticação Multi-Tenant

## Status

Aceita.

## Contexto

A plataforma precisa autenticar usuários em ambiente multi-tenant sem depender ainda dos módulos completos de empresas e usuários.

## Decisão

Usar login com `tenant`, `email` e `password`.

O backend resolve internamente o `tenant_id` a partir de uma representação técnica mínima (`tenant_slug`) na tabela `auth_users`.

Access tokens serão JWTs curtos com claims obrigatórias. Refresh tokens serão opacos, rotacionáveis e persistidos apenas como hash.

## Consequências

- O cliente não controla `tenant_id`.
- O sistema já fica preparado para isolamento por tenant.
- O módulo de empresas poderá substituir o resolver mínimo em task futura.
- Reuso de refresh token revogado é detectado e auditado.
