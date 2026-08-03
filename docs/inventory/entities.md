# Inventory Entities

## InventoryBalance

Projeção atual de saldo por:

- tenant;
- filial;
- produto;
- warehouse;
- location reservado.

Campos principais:

- `physical_quantity`;
- `reserved_quantity`;
- `putaway_pending_quantity`;
- `available_quantity`.

`available_quantity` é calculado como:

```text
physical_quantity - reserved_quantity - putaway_pending_quantity
```

## InventoryMovement

Histórico imutável de mudanças.

Tipos REST-003:

- `receipt`;
- `putaway`;
- `adjustment_in`;
- `adjustment_out`;
- `reservation_created`;
- `reservation_released`.

Campos:

- delta físico;
- delta reservado;
- delta pendente de put away;
- motivo;
- origem;
- `origin_module`;
- `business_process`;
- evento planejado;
- ator.

## InventoryAdjustment

Operação de ajuste.

Tipos:

- `increase`;
- `decrease`.

Todo ajuste confirmado gera movimento.

## InventoryReservation

Bloqueio lógico de saldo disponível.

Estados REST-003:

- `active`;
- `released`;
- `cancelled` reservado.

Reserva ativa aumenta `reserved_quantity` e reduz disponibilidade, sem alterar `physical_quantity`.

## ReceivingDocument

Documento de recebimento de mercadorias.

Campos principais:

- `warehouse_id`;
- `supplier_id` preparado;
- `document_number`;
- `document_type`;
- `status`;
- `expected_date`;
- `received_date`;
- `notes`.

Estados REST-007:

- `draft`;
- `expected`;
- `receiving`;
- `partial`;
- `received`;
- `cancelled`.

## ReceivingItem

Item do documento de recebimento.

Campos principais:

- `product_id`;
- `ordered_quantity`;
- `received_quantity`;
- `damaged_quantity`;
- `pending_quantity`;
- `unit_cost`.

`pending_quantity` é derivado de `ordered_quantity - received_quantity - damaged_quantity`.

## GoodsReceipt

Serviço de aplicação da REST-008.

Ele não é uma entidade persistida própria nesta versão. A confirmação gera:

- status `putaway_pending` no `ReceivingDocument`;
- `InventoryMovement` do tipo `receipt`;
- atualização projetada em `InventoryBalance`.

## PutAwayService

Serviço de aplicação da REST-009.

Ele não cria entidade persistida própria nesta versão. A confirmação gera:

- `InventoryMovement` do tipo `putaway`;
- redução de `putaway_pending_quantity`;
- liberação do saldo na `WarehouseLocation` final;
- status `available` quando o documento fica sem pendência;
- rastreabilidade por `origin_module` e `business_process`.

## Warehouse E Location

`warehouse_id` referencia `warehouses.id` a partir da REST-004.

`location_id` referencia Warehouse Location a partir da REST-006.
