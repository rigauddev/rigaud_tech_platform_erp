# Eventos Do Inventory Engine

O Inventory Engine deve publicar eventos internos estáveis.

Kafka é planejado para o futuro, mas a primeira implementação deve usar dispatcher interno desacoplado.

## Eventos Internos

- `inventory.created`;
- `inventory.updated`;
- `inventory.adjusted`;
- `inventory.transferred`;
- `inventory.reserved`;
- `inventory.released`;
- `inventory.count.finished`;
- `inventory.low.stock`;
- `inventory.out.of.stock`.

## Eventos Kafka Planejados

Os nomes dos tópicos/eventos devem preservar os mesmos nomes internos.

Contrato mínimo planejado:

```json
{
  "event_id": "uuid",
  "event_name": "inventory.adjusted",
  "tenant_id": "uuid",
  "branch_id": "uuid",
  "entity_id": "uuid",
  "occurred_at": "2026-08-01T12:00:00Z",
  "source_module": "inventory",
  "schema_version": 1,
  "payload": {}
}
```

## Eventos Consumidos Futuramente

Product:

- `product.created`;
- `product.updated`;
- `product.deleted`.

Order:

- `order.created`;
- `order.cancelled`;
- `order.closed`.

Sales/POS:

- `sale.finished`;
- `sale.cancelled`;
- `sale.returned`.

Delivery:

- `delivery.dispatched`;
- `delivery.cancelled`.

## Event Store

DOC-005 não implementa Event Sourcing.

Ela recomenda preparar um futuro módulo Core Events com:

- dispatcher interno;
- handlers por módulo;
- envelope padronizado;
- idempotência;
- outbox pattern futuro;
- substituição futura por Kafka sem alterar contratos de domínio.

