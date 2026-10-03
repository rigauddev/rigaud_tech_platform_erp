# Inventory Transactions

REST-010 oficializa `InventoryMovement` como livro razao operacional do Inventory Engine.

## Objetivo

Permitir consulta auditavel de todas as transacoes que alteram ou comprometem saldo.

Nesta task, transacao de estoque e uma visao operacional imutavel sobre `InventoryMovement`.

## Regra Central

`InventoryBalance` continua sendo uma projecao.

Nenhuma funcionalidade deve alterar saldo sem registrar `InventoryMovement`.

## Endpoints

```text
GET /api/v1/inventory/transactions
GET /api/v1/inventory/transactions/{transaction_id}
```

## Filtros

`GET /transactions` aceita:

- `page`;
- `page_size`;
- `branch_id`;
- `product_id`;
- `warehouse_id`;
- `location_id`;
- `movement_type`;
- `origin_module`;
- `business_process`;
- `source_module`.

Filtros de `origin_module` e `business_process` sao normalizados para maiusculas no backend.

`source_module` e normalizado para minusculas.

## Resposta

Cada transacao retorna:

- identificadores de tenant, filial, produto, warehouse e location;
- tipo de movimento;
- status;
- deltas de quantidade;
- motivo;
- origem funcional;
- processo de negocio;
- evento interno;
- ator;
- `immutable=true`.

## Imutabilidade

Movimento confirmado nao e editado.

Correcoes devem gerar nova transacao.

Exemplos:

- ajuste;
- estorno futuro;
- transferencia futura;
- inventario futuro;
- perda futura.

## Impacto Futuro

As transacoes serao usadas por:

- restaurante;
- varejo;
- financeiro;
- fiscal;
- relatorios;
- auditoria;
- AI/MCP;
- Kafka futuro;
- offline sync futuro.

## Referencias Consultadas

- Microsoft Business Central Put-away: https://learn.microsoft.com/en-us/dynamics365/business-central/warehouse-how-to-put-items-away-with-warehouse-put-aways

## Fora Do Escopo

REST-010 nao implementa:

- Inventory Count;
- Stock Adjustments avancados;
- Transfers;
- venda;
- restaurante;
- financeiro;
- Kafka;
- Event Store.
