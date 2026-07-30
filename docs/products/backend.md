# Products Backend

O backend de Products segue Clean Architecture simplificada, DDD, Repository Pattern e Use Case Pattern.

## Tenant

`Product.tenant_id` referencia `Company.id`.

O tenant é derivado do usuário autenticado. A API não aceita `tenant_id` livre no payload de produtos.

Produtos de outro tenant são tratados como não encontrados.

## Endpoints

- `POST /api/v1/products`
- `GET /api/v1/products`
- `GET /api/v1/products/{product_id}`
- `PATCH /api/v1/products/{product_id}`
- `POST /api/v1/products/{product_id}/activate`
- `POST /api/v1/products/{product_id}/deactivate`
- `POST /api/v1/products/{product_id}/availability`
- `DELETE /api/v1/products/{product_id}`

## Valores monetários

O backend usa `Decimal` e PostgreSQL `NUMERIC(12, 2)`.

Não usar `float` em regras monetárias.

## Unicidade

Garantias:

- `tenant_id + internal_code`;
- `tenant_id + barcode`, somente quando `barcode` não é nulo.

Erros de unicidade retornam `PRODUCT_ALREADY_EXISTS`.

## Soft Delete

Produtos removidos recebem `deleted_at`, ficam inativos e indisponíveis para venda.

Consultas normais não retornam produtos excluídos.
