import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_error.dart';
import '../domain/warehouse_zone.dart';
import '../domain/warehouse_zone_input.dart';
import '../domain/warehouse_zone_repository.dart';
import 'warehouse_zone_remote_data_source.dart';

class WarehouseZoneRepositoryImpl implements WarehouseZoneRepository {
  const WarehouseZoneRepositoryImpl(this._remote);

  final WarehouseZoneRemoteDataSource _remote;

  @override
  Future<List<WarehouseZone>> list({
    String? warehouseId,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) {
    return _guard(
      () => _remote.list(
        warehouseId: warehouseId,
        isActive: isActive,
        page: page,
        pageSize: pageSize,
      ),
    );
  }

  @override
  Future<WarehouseZone> get(String id) => _guard(() => _remote.get(id));

  @override
  Future<WarehouseZone> create(WarehouseZoneInput input) =>
      _guard(() => _remote.create(input));

  @override
  Future<WarehouseZone> update(String id, WarehouseZoneInput input) {
    return _guard(() => _remote.update(id, input));
  }

  @override
  Future<WarehouseZone> reorder(String id, int sortOrder) {
    return _guard(() => _remote.reorder(id, sortOrder));
  }

  @override
  Future<WarehouseZone> delete(String id) => _guard(() => _remote.delete(id));

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw mapDioError(error);
    } catch (error) {
      throw ApiError(error.toString(), code: 'WAREHOUSE_ZONES_CLIENT_ERROR');
    }
  }
}

final warehouseZoneRepositoryProvider = Provider<WarehouseZoneRepository>((
  ref,
) {
  return WarehouseZoneRepositoryImpl(
    ref.watch(warehouseZoneRemoteDataSourceProvider),
  );
});
