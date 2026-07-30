# Academy: Cadastro de Produtos Multi-Tenant

REST-001 introduz o primeiro cadastro comercial do ERP.

O produto pertence ao Core porque será reutilizado por Restaurante, Fashion e módulos futuros.

## Decisão principal

Produto é tenant-aware:

```text
Product.tenant_id = Company.id
```

O frontend não envia `tenant_id`. O backend deriva o tenant a partir do usuário autenticado.

## Dinheiro

Preços e custos usam:

- `Decimal` no backend;
- `NUMERIC(12, 2)` no PostgreSQL;
- string segura no contrato JSON;
- formatação pt-BR no Flutter.

`float` não deve ser usado para dinheiro.

Valores são normalizados para duas casas decimais.

## Status

`status` representa o estado funcional.

`is_available_for_sale` representa disponibilidade comercial.

Ativar um produto não deve disponibilizá-lo automaticamente.

## Exclusão lógica

Produtos removidos permanecem no banco com `deleted_at`.

Isso preserva rastreabilidade para auditoria e histórico futuro de vendas.

## Limite da REST-001

Categorias, estoque, cardápio, ingredientes e pedidos pertencem a tasks futuras.
