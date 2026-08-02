# Inventory

Módulo do Inventory Engine.

Estrutura independente preparada com camadas `application`, `domain`, `infrastructure`, `presentation` e `tests`.

DOC-005 congela o domínio do Inventory Engine antes da REST-003.

REST-003 implementa a primeira versão executável:

- `InventoryBalance`;
- `InventoryMovement`;
- `InventoryAdjustment`;
- `InventoryReservation`;
- endpoints em `/api/v1/inventory/*`;
- auditoria de ajustes e reservas;
- eventos internos preparados para Kafka futuro.

REST-004 adiciona Warehouse Management:

- `Warehouse`;
- CRUD em `/api/v1/warehouses`;
- depósito padrão por filial;
- soft delete;
- auditoria;
- validação de `warehouse_id` em ajustes e reservas.

REST-005 adiciona Warehouse Zones:

- `WarehouseZone`;
- CRUD em `/api/v1/warehouse-zones`;
- tipos operacionais;
- flags para recebimento, expedição, armazenagem, produção e quarentena;
- ordenação;
- soft delete;
- auditoria.

REST-006 adiciona Warehouse Locations:

- `WarehouseLocation`;
- CRUD em `/api/v1/warehouse-locations`;
- filtros por depósito, zona e pesquisa;
- QR Code e código de barras preparados;
- ativação e inativação;
- ordenação;
- soft delete;
- auditoria.

Documentação principal:

- `docs/inventory/overview.md`
- `docs/inventory/api.md`
- `docs/inventory/endpoints.md`
- `docs/inventory/entities.md`
- `docs/inventory/domain-model.md`
- `docs/inventory/events.md`
- `docs/inventory/permissions.md`
- `docs/inventory/validation.md`
- `docs/warehouse/overview.md`
- `docs/warehouse/zones.md`
- `docs/warehouse/locations.md`
- `docs/inventory/offline-strategy.md`
