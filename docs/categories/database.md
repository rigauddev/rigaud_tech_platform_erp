# Categories Database

REST-002 adiciona a tabela `categories`.

## Tabela

Campos principais:

- `id`
- `tenant_id`
- `parent_id`
- `internal_code`
- `name`
- `slug`
- `description`
- `icon`
- `color`
- `display_order`
- `status`
- `is_active`
- `created_at`
- `updated_at`
- `deleted_at`
- `created_by`
- `updated_by`
- `deleted_by`

## Constraints

- `tenant_id + slug` único.
- `tenant_id + internal_code` único.
- `display_order >= 0`.
- `parent_id` referencia `categories.id`.
- `tenant_id` referencia `companies.id`.

## Migration

```text
0010_product_categories
```

Esta migration não cria tabelas de estoque, cardápio ou vínculo com produtos.
