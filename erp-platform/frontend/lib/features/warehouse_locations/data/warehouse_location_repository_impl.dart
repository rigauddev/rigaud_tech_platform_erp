import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/warehouse_location.dart';
import '../domain/warehouse_location_input.dart';
import '../domain/warehouse_location_repository.dart';
import 'warehouse_location_remote_data_source.dart';

class WarehouseLocationRepositoryImpl implements WarehouseLocationRepository {
  const WarehouseLocationRepositoryImpl(this._dataSource);

  final WarehouseLocationRemoteDataSource _dataSource;

  @override
  Future<List<WarehouseLocation>> list({
    String? warehouseId,
    String? zoneId,
    String? search,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) {
    return _dataSource.list(
      warehouseId: warehouseId,
      zoneId: zoneId,
      search: search,
      isActive: isActive,
      page: page,
      pageSize: pageSize,
    );
  }

  @override
  Future<WarehouseLocation> get(String id) {
    return _dataSource.get(id);
  }

  @override
  Future<WarehouseLocation> create(WarehouseLocationInput input) {
    return _dataSource.create(input);
  }

  @override
  Future<WarehouseLocation> update(String id, WarehouseLocationInput input) {
    return _dataSource.update(id, input);
  }

  @override
  Future<WarehouseLocation> activate(String id) {
    return _dataSource.activate(id);
  }

  @override
  Future<WarehouseLocation> deactivate(String id) {
    return _dataSource.deactivate(id);
  }

  @override
  Future<WarehouseLocation> reorder(String id, int sortOrder) {
    return _dataSource.reorder(id, sortOrder);
  }

  @override
  Future<WarehouseLocation> delete(String id) {
    return _dataSource.delete(id);
  }
}

final warehouseLocationRepositoryProvider =
    Provider<WarehouseLocationRepository>((ref) {
      return WarehouseLocationRepositoryImpl(
        ref.watch(warehouseLocationRemoteDataSourceProvider),
      );
    });
