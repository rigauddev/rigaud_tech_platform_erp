import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_error.dart';
import '../domain/warehouse.dart';
import '../domain/warehouse_input.dart';
import '../domain/warehouse_repository.dart';
import 'warehouse_remote_data_source.dart';

class WarehouseRepositoryImpl implements WarehouseRepository {
  const WarehouseRepositoryImpl(this._remote);

  final WarehouseRemoteDataSource _remote;

  @override
  Future<List<Warehouse>> list({
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) {
    return _guard(
      () => _remote.list(isActive: isActive, page: page, pageSize: pageSize),
    );
  }

  @override
  Future<Warehouse> get(String id) => _guard(() => _remote.get(id));

  @override
  Future<Warehouse> create(WarehouseInput input) =>
      _guard(() => _remote.create(input));

  @override
  Future<Warehouse> update(String id, WarehouseInput input) {
    return _guard(() => _remote.update(id, input));
  }

  @override
  Future<Warehouse> setDefault(String id) =>
      _guard(() => _remote.setDefault(id));

  @override
  Future<Warehouse> delete(String id) => _guard(() => _remote.delete(id));

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw mapDioError(error);
    } catch (error) {
      throw ApiError(error.toString(), code: 'WAREHOUSES_CLIENT_ERROR');
    }
  }
}

final warehouseRepositoryProvider = Provider<WarehouseRepository>((ref) {
  return WarehouseRepositoryImpl(ref.watch(warehouseRemoteDataSourceProvider));
});
