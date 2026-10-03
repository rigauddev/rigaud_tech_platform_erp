# Warehouse Database

Migration:

```text
0013_warehouses
```

## Tabela warehouses

Campos:

- `id`;
- `tenant_id`;
- `branch_id`;
- `code`;
- `name`;
- `description`;
- `address`;
- `status`;
- `is_default`;
- `is_active`;
- `created_at`;
- `updated_at`;
- `deleted_at`;
- `created_by`;
- `updated_by`;
- `deleted_by`.

## Índices

- único por `tenant_id`, `branch_id`, `code`;
- único parcial para depósito padrão por filial;
- consulta por tenant e filial;
- consulta por tenant e ativo.

## FKs

REST-004 adiciona foreign keys de `warehouse_id` para `warehouses.id` nas tabelas do Inventory Engine.

## Soft Delete

Depósitos removidos recebem `deleted_at` e deixam de aparecer nas consultas.

## Documentação Relacionada

- Zonas: `docs/warehouse/zones-database.md`;
- Localizações: `docs/warehouse/locations-database.md`.
