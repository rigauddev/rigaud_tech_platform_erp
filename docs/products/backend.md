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

## Status e disponibilidade

`status` é a fonte funcional de estado do produto:

- `active`;
- `inactive`.

`is_active` permanece como compatibilidade operacional e acompanha `status`.

`is_available_for_sale` é separado do status. Um produto ativo pode estar indisponível. Produto inativo ou excluído não pode ficar disponível.

Ativar um produto não torna o item automaticamente disponível para venda.

## Valores monetários

O backend usa `Decimal` e PostgreSQL `NUMERIC(12, 2)`.

Não usar `float` em regras monetárias.

Valores são normalizados para duas casas decimais. A API deve receber valores numéricos simples, como `25.90`, não valores formatados como `R$ 25,90`.

## Unicidade

Garantias:

- `tenant_id + internal_code`;
- `tenant_id + barcode`, somente quando `barcode` não é nulo.

Erros de unicidade retornam:

- `PRODUCT_INTERNAL_CODE_ALREADY_EXISTS`;
- `PRODUCT_BARCODE_ALREADY_EXISTS`.

## Soft Delete

Produtos removidos recebem `deleted_at`, ficam inativos e indisponíveis para venda.

Consultas normais não retornam produtos excluídos.

## Imagem principal

A REST-001 armazena somente uma URL em `main_image_url`.

Upload de arquivo, armazenamento binário, limpeza de arquivos e adapter de mídia ficam fora do escopo.
