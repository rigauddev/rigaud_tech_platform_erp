# Warehouse Zones Database

Migration:

```text
0014_warehouse_zones
```

## Tabela

```text
warehouse_zones
```

Campos:

- `id`;
- `tenant_id`;
- `branch_id`;
- `warehouse_id`;
- `code`;
- `name`;
- `description`;
- `type`;
- `color`;
- `icon`;
- `sort_order`;
- `is_receiving`;
- `is_shipping`;
- `is_storage`;
- `is_production`;
- `is_quarantine`;
- `status`;
- `is_active`;
- timestamps;
- auditoria;
- `deleted_at`.

## Constraints

- FK para `companies.id`;
- FK para `branches.id`;
- FK para `warehouses.id`;
- índice único parcial por `tenant_id`, `warehouse_id` e `code` quando `deleted_at IS NULL`.

## Soft Delete

Zonas removidas recebem `deleted_at` e deixam de aparecer nas consultas.

O código pode ser reaproveitado após remoção lógica porque o índice único ignora registros removidos.
