# Products Database

Migration:

```text
0008_products
```

Tabela:

```text
products
```

Campos técnicos:

- `id`;
- `tenant_id`;
- `created_at`;
- `updated_at`;
- `deleted_at`;
- `created_by`;
- `updated_by`;
- `deleted_by`.

Campos do cadastro:

- `name`;
- `description`;
- `internal_code`;
- `barcode`;
- `product_type`;
- `unit_of_measure`;
- `status`;
- `sale_price`;
- `cost_price`;
- `main_image_url`;
- `is_active`;
- `is_available_for_sale`.

Índices e constraints preservam isolamento por tenant, unicidade e valores monetários não negativos.

`status` é armazenado como enum técnico `product_status`.
