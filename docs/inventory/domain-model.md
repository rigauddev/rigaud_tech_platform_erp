# Modelo De Domínio

## Warehouse

Representa uma unidade lógica de estoque dentro de um tenant.

Campos planejados:

- `id`;
- `tenant_id`;
- `branch_id`;
- `code`;
- `name`;
- `description`;
- `status`;
- auditoria e timestamps.

Regras:

- `code` deve ser único por tenant e filial;
- um warehouse pertence a uma única filial;
- warehouse inativo não recebe novas operações;
- warehouse inativo pode manter histórico.

## WarehouseZone

Representa uma zona operacional dentro de um warehouse.

Campos REST-005:

- `id`;
- `tenant_id`;
- `branch_id`;
- `warehouse_id`;
- `code`;
- `name`;
- `description`;
- `type`;
- `color`;
- `icon`;
- `sort_order`;
- flags operacionais;
- `status`;
- auditoria e timestamps.

Regras:

- `code` deve ser único por warehouse entre zonas não removidas;
- uma zona pertence a um único warehouse;
- o warehouse precisa pertencer ao tenant e à filial ativa;
- zona inativa não recebe novas localizações.

## WarehouseLocation

Representa um endereço físico dentro de uma zona de depósito.

Também é o `Stock Location` ou `Bin` operacional do ERP.

Campos REST-006:

- identificação por UUID e código curto;
- vínculo com `tenant_id`, `branch_id`, `warehouse_id` e `zone_id`;
- `alias`;
- `barcode`;
- `qr_code`;
- atributos físicos: corredor, rack, prateleira, nível e posição;
- capacidade e unidade de capacidade;
- flags operacionais para recebimento, picking e expedição;
- flags de política preparatória para saldo negativo, itens mistos e vencidos;
- status, ordenação, soft delete, auditoria e timestamps.

Regras:

- `code` deve ser único por warehouse entre localizações não removidas;
- `barcode` e `qr_code` devem ser únicos por tenant quando informados;
- um local pertence a uma única zona;
- a zona deve pertencer ao mesmo warehouse;
- movimentações devem informar local quando o warehouse exigir controle por localização.

## InventoryBalance

Representa saldo agregado por produto, filial, warehouse e local.

Campos planejados:

- `id`;
- `tenant_id`;
- `branch_id`;
- `product_id`;
- `warehouse_id`;
- `location_id`;
- `quantity_on_hand`;
- `quantity_reserved`;
- `quantity_available`;
- `minimum_quantity`;
- `maximum_quantity`;
- `reorder_point`;
- `last_movement_at`;
- auditoria e timestamps.

Regras:

- `quantity_available = quantity_on_hand - quantity_reserved`;
- saldo físico não pode ficar negativo sem política explícita futura;
- reserva não pode exceder saldo disponível;
- saldo deve ser recalculável a partir de transações e movimentos.

## InventoryMovement

Representa mudança operacional de saldo.

Campos planejados:

- `id`;
- `tenant_id`;
- `branch_id`;
- `product_id`;
- `warehouse_id`;
- `location_id`;
- `movement_type`;
- `quantity`;
- `unit_cost`;
- `source_module`;
- `source_id`;
- `reason`;
- `occurred_at`;
- auditoria e timestamps.

Regras:

- movimento confirmado é imutável;
- correções devem gerar novo movimento;
- todo movimento deve gerar uma `InventoryTransaction`.

## InventoryReservation

Representa bloqueio lógico de saldo disponível.

Estados:

- `pending`;
- `active`;
- `released`;
- `consumed`;
- `expired`;
- `cancelled`.

Regras:

- reserva ativa reduz disponibilidade;
- reserva consumida gera movimento de saída;
- reserva expirada libera disponibilidade;
- reserva deve ser vinculada a uma origem estável.

## InventoryAdjustment

Representa ajuste manual ou técnico de saldo.

Regras:

- ajuste exige motivo;
- ajuste pode exigir aprovação em configuração futura;
- ajuste confirmado gera movimento `ADJUSTMENT`.

## InventoryCount

Representa inventário ou contagem física.

Estados:

- `draft`;
- `in_progress`;
- `finished`;
- `cancelled`.

Regras:

- contagem finalizada pode gerar ajustes;
- contagem cancelada não altera saldo;
- histórico de divergências deve ser preservado.

## InventoryTransfer

Representa transferência entre warehouses ou locations.

Estados:

- `draft`;
- `requested`;
- `in_transit`;
- `received`;
- `cancelled`.

Regras:

- saída e entrada devem ser rastreadas separadamente;
- transferência entre filiais deve preservar tenant;
- divergências de recebimento devem gerar ajuste ou pendência.

## InventoryTransaction

Registro técnico imutável para rastreabilidade e reconstrução de saldo.

Regras:

- transação é append-only;
- `idempotency_key` evita duplicidade em retries e sincronização futura;
- transações serão a base para relatórios e conciliação.
