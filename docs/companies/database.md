# Companies Database

## Tabela

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
