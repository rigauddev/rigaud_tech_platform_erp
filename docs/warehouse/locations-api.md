# Warehouse Locations API

Base path:

```text
/api/v1/warehouse-locations
```

Todos os endpoints usam o envelope padrão da plataforma.

## Endpoints

```text
GET    /api/v1/warehouse-locations
GET    /api/v1/warehouse-locations/{location_id}
POST   /api/v1/warehouse-locations
PUT    /api/v1/warehouse-locations/{location_id}
POST   /api/v1/warehouse-locations/{location_id}/activate
POST   /api/v1/warehouse-locations/{location_id}/deactivate
POST   /api/v1/warehouse-locations/{location_id}/reorder
DELETE /api/v1/warehouse-locations/{location_id}
```

## Filtros

`GET /api/v1/warehouse-locations` aceita:

- `warehouse_id`;
- `zone_id`;
- `search`;
- `is_active`;
- `page`;
- `page_size`.

## Payload

Campos principais:

- `warehouse_id`;
- `zone_id`;
- `code`;
- `name`;
- `alias`;
- `barcode`;
- `qr_code`;
- `aisle`;
- `rack`;
- `shelf`;
- `level`;
- `position`;
- `capacity`;
- `capacity_unit`;
- `allow_negative`;
- `allow_mixed_items`;
- `allow_expired`;
- `is_pick_location`;
- `is_receive_location`;
- `is_shipping_location`;
- `is_default`;
- `sort_order`;
- `is_active`.

## Códigos

- `WAREHOUSE_LOCATION_CREATED`;
- `WAREHOUSE_LOCATION_UPDATED`;
- `WAREHOUSE_LOCATION_ACTIVATED`;
- `WAREHOUSE_LOCATION_DEACTIVATED`;
- `WAREHOUSE_LOCATION_DELETED`;
- `WAREHOUSE_LOCATION_REORDERED`;
- `WAREHOUSE_LOCATION_RETRIEVED`;
- `WAREHOUSE_LOCATION_LIST_RETRIEVED`;
- `WAREHOUSE_LOCATION_NOT_FOUND`;
- `WAREHOUSE_LOCATION_CODE_ALREADY_EXISTS`;
- `WAREHOUSE_LOCATION_BARCODE_ALREADY_EXISTS`;
- `WAREHOUSE_LOCATION_QR_CODE_ALREADY_EXISTS`;
- `WAREHOUSE_LOCATION_BRANCH_REQUIRED`;
- `WAREHOUSE_LOCATION_INVALID_DATA`.
