# Companies Database

## Tabelas

`companies`

Campos principais:

- `id`
- `legal_name`
- `trade_name`
- `document`
- `email`
- `phone`
- `slug`
- `code`
- `status`
- `timezone`
- `locale`
- `currency`
- `is_active`
- timestamps
- soft delete
- auditoria básica

## Constraints

- `document` único.
- `slug` único.
- `code` único.
- `document` com 14 dígitos.
- `status` restrito a `active`, `inactive`, `suspended`.

`Company` não possui `tenant_id`.

O `company.id` é o `tenant_id` das entidades tenant-aware.

`branches`

Campos principais:

- `id`
- `tenant_id`
- `name`
- `code`
- `document`
- `type`
- `status`
- `is_active`
- timestamps
- soft delete
- auditoria básica

`company_memberships`

Campos principais:

- `id`
- `tenant_id`
- `user_id`
- `role`
- `status`
- `access_scope`
- `is_default`
- timestamps
- auditoria básica

`branch_memberships`

Campos principais:

- `id`
- `tenant_id`
- `company_membership_id`
- `branch_id`
- `role`
- `status`
- `is_default`
- timestamps
- auditoria básica

`auth_sessions`

Na DEV-010, sessões passam a guardar contexto opcional para preservar refresh token:

- `membership_id`
- `branch_id`
- `branch_membership_id`
- `role`
- `access_scope`

## Migration

`0009_tenant_context` cria as tabelas técnicas de filiais e memberships.

A migration também cria uma filial matriz padrão para empresas existentes e memberships técnicos iniciais para usuários existentes.

A integridade operacional exige que `branch_memberships.branch_id` pertença ao mesmo `tenant_id` do `company_memberships.tenant_id`.
