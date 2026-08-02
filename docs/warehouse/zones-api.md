# Warehouse Zones API

Base path:

```text
/api/v1/warehouse-zones
```

Endpoints:

```text
GET    /warehouse-zones
GET    /warehouse-zones/{zone_id}
POST   /warehouse-zones
PUT    /warehouse-zones/{zone_id}
POST   /warehouse-zones/{zone_id}/reorder
DELETE /warehouse-zones/{zone_id}
```

## Payload

```json
{
  "warehouse_id": "uuid",
  "code": "REC",
  "name": "Recebimento",
  "description": "Conferência inicial de mercadorias.",
  "type": "receiving",
  "color": "#2B6CB0",
  "icon": "assignment_returned",
  "sort_order": 10,
  "is_receiving": true,
  "is_shipping": false,
  "is_storage": false,
  "is_production": false,
  "is_quarantine": false,
  "is_active": true
}
```

## Respostas

Todas as respostas usam o envelope padrão da plataforma.

Códigos principais:

- `WAREHOUSE_ZONE_CREATED`;
- `WAREHOUSE_ZONE_UPDATED`;
- `WAREHOUSE_ZONE_DELETED`;
- `WAREHOUSE_ZONE_REORDERED`;
- `WAREHOUSE_ZONE_RETRIEVED`;
- `WAREHOUSE_ZONE_LIST_RETRIEVED`;
- `WAREHOUSE_ZONE_NOT_FOUND`;
- `WAREHOUSE_ZONE_CODE_ALREADY_EXISTS`;
- `WAREHOUSE_ZONE_BRANCH_REQUIRED`;
- `WAREHOUSE_ZONE_INVALID_DATA`;
- `WAREHOUSE_NOT_FOUND`;
- `WAREHOUSE_INACTIVE`.

## Eventos

Eventos internos preparados para Kafka futuro:

- `warehouse_zone.created`;
- `warehouse_zone.updated`;
- `warehouse_zone.reordered`;
- `warehouse_zone.deleted`.
