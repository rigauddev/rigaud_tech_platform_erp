import 'warehouse.dart';
import 'warehouse_input.dart';

abstract interface class WarehouseRepository {
  Future<List<Warehouse>> list({
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  });

  Future<Warehouse> get(String id);

  Future<Warehouse> create(WarehouseInput input);

  Future<Warehouse> update(String id, WarehouseInput input);

  Future<Warehouse> setDefault(String id);

  Future<Warehouse> delete(String id);
}
