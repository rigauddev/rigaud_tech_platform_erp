import 'warehouse_zone.dart';
import 'warehouse_zone_input.dart';

abstract interface class WarehouseZoneRepository {
  Future<List<WarehouseZone>> list({
    String? warehouseId,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  });

  Future<WarehouseZone> get(String id);

  Future<WarehouseZone> create(WarehouseZoneInput input);

  Future<WarehouseZone> update(String id, WarehouseZoneInput input);

  Future<WarehouseZone> reorder(String id, int sortOrder);

  Future<WarehouseZone> delete(String id);
}
