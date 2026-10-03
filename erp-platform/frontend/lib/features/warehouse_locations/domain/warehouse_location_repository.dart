import 'warehouse_location.dart';
import 'warehouse_location_input.dart';

abstract class WarehouseLocationRepository {
  Future<List<WarehouseLocation>> list({
    String? warehouseId,
    String? zoneId,
    String? search,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  });

  Future<WarehouseLocation> get(String id);

  Future<WarehouseLocation> create(WarehouseLocationInput input);

  Future<WarehouseLocation> update(String id, WarehouseLocationInput input);

  Future<WarehouseLocation> activate(String id);

  Future<WarehouseLocation> deactivate(String id);

  Future<WarehouseLocation> reorder(String id, int sortOrder);

  Future<WarehouseLocation> delete(String id);
}
