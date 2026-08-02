# Eventos Do Inventory Engine

O Inventory Engine deve publicar eventos internos estáveis.

REST-007 prepara eventos de documento de recebimento para Kafka futuro, mas ainda não publica em broker externo.

Eventos planejados:

- `receiving_document.created`;
- `receiving_document.updated`;
- `receiving_document.status_changed`;
- `receiving_document.deleted`.

Kafka é planejado para o futuro, mas a primeira implementação deve usar dispatcher interno desacoplado.

## Eventos Internos

- `inventory.adjusted.in`;
- `inventory.adjusted.out`;
- `inventory.reserved`;
- `inventory.reservation.released`;
- `inventory.transferred`;
- `inventory.count.finished`;
- `inventory.low.stock`;
- `inventory.out.of.stock`.

REST-003 implementa os quatro primeiros eventos. Os demais permanecem planejados.

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
