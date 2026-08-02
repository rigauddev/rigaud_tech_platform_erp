# Receiving Database

REST-007 adiciona a migration:

```text
0016_receiving_documents
```

## Tabelas

`receiving_documents`:

- `id`;
- `tenant_id`;
- `branch_id`;
- `warehouse_id`;
- `supplier_id`;
- `document_number`;
- `document_type`;
- `status`;
- `expected_date`;
- `received_date`;
- `notes`;
- auditoria;
- timestamps;
- soft delete.

`receiving_items`:

- `id`;
- `tenant_id`;
- `document_id`;
- `product_id`;
- `ordered_quantity`;
- `received_quantity`;
- `damaged_quantity`;
- `pending_quantity`;
- `unit_cost`;
- timestamps.

## Índices

- documento único por `tenant_id`, `branch_id` e `document_number` enquanto não excluído;
- consultas por filial;
- consultas por warehouse;
- consultas por status;
- itens por documento;
- itens por produto.

## Limite

As tabelas de recebimento não atualizam `inventory_balances` e não criam `inventory_movements`.
