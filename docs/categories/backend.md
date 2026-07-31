# Categories Backend

O backend de Categories segue Clean Architecture simplificada, DDD, Repository Pattern e Use Case Pattern.

## Tenant

`Category.tenant_id` referencia `Company.id`.

O tenant é derivado do usuário autenticado. A API não aceita `tenant_id` livre no payload.

Categorias de outro tenant são tratadas como não encontradas.

## Endpoints

- `POST /api/v1/categories`
- `GET /api/v1/categories`
- `GET /api/v1/categories/{category_id}`
- `PATCH /api/v1/categories/{category_id}`
- `POST /api/v1/categories/{category_id}/activate`
- `POST /api/v1/categories/{category_id}/deactivate`
- `POST /api/v1/categories/{category_id}/reorder`
- `DELETE /api/v1/categories/{category_id}`

## Filtros

`GET /api/v1/categories` aceita:

- `status`
- `search`
- `parent`
- `ordering`
- `tree`
- `page`
- `page_size`

## Hierarquia

`parent_id` permite árvores sem profundidade fixa.

O backend valida ciclos ao alterar o pai de uma categoria.

## Auditoria

Eventos registrados:

- `category.created`
- `category.updated`
- `category.deleted`
- `category.activated`
- `category.deactivated`
- `category.reordered`
