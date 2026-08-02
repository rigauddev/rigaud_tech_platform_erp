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
- `available_quantity`.

`available_quantity` é calculado como:

```text
physical_quantity - reserved_quantity
```

## InventoryMovement

Histórico imutável de mudanças.

Tipos REST-003:

- `adjustment_in`;
- `adjustment_out`;
- `reservation_created`;
- `reservation_released`.

Campos:

- delta físico;
- delta reservado;
- motivo;
- origem;
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

## Warehouse E Location

`warehouse_id` referencia `warehouses.id` a partir da REST-004.

`location_id` permanece reservado para REST-005, quando o cadastro de Stock Locations será implementado.
