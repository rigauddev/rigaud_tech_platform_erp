# Warehouse Locations Database

Migration:

```text
0015_warehouse_locations
```

Tabela:

```text
warehouse_locations
```

## Campos

- `id`;
- `tenant_id`;
- `branch_id`;
- `warehouse_id`;
- `zone_id`;
- `code`;
- `name`;
- `alias`;
- `barcode`;
- `qr_code`;
- `aisle`;
- `rack`;
- `shelf`;
- `level`;
- `position`;
- `capacity`;
- `capacity_unit`;
- `allow_negative`;
- `allow_mixed_items`;
- `allow_expired`;
- `is_pick_location`;
- `is_receive_location`;
- `is_shipping_location`;
- `is_default`;
- `sort_order`;
- `status`;
- `is_active`;
- `created_at`;
- `updated_at`;
- `deleted_at`;
- `created_by`;
- `updated_by`;
- `deleted_by`.

## Índices

- único por `tenant_id`, `warehouse_id` e `code` para registros não removidos;
- único por `tenant_id` e `barcode` quando `barcode` existe;
- único por `tenant_id` e `qr_code` quando `qr_code` existe;
- busca por tenant/filial;
- busca por tenant/warehouse;
- busca por tenant/zone;
- busca por tenant/status ativo.

## Limites

A REST-006 não altera saldos, movimentos, reservas ou ajustes. O vínculo entre localização e operação de estoque será usado pelas próximas tasks de entrada, transferência, contagem e picking.
