import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_error.dart';
import '../domain/inventory.dart';
import '../domain/inventory_input.dart';
import '../domain/inventory_repository.dart';
import 'inventory_remote_data_source.dart';

class InventoryRepositoryImpl implements InventoryRepository {
  const InventoryRepositoryImpl(this._remote);

  final InventoryRemoteDataSource _remote;

  @override
  Future<List<InventoryBalance>> listBalances({
    String? productId,
    int page = 1,
    int pageSize = 20,
  }) {
    return _guard(
      () => _remote.listBalances(
        productId: productId,
        page: page,
        pageSize: pageSize,
      ),
    );
  }

  @override
  Future<List<InventoryMovement>> listMovements({
    String? productId,
    int page = 1,
    int pageSize = 20,
  }) {
    return _guard(
      () => _remote.listMovements(
        productId: productId,
        page: page,
        pageSize: pageSize,
      ),
    );
  }

  @override
  Future<InventoryOperation> createAdjustment(InventoryAdjustmentInput input) {
    return _guard(() => _remote.createAdjustment(input));
  }

  @override
  Future<InventoryOperation> createReservation(
    InventoryReservationInput input,
  ) {
    return _guard(() => _remote.createReservation(input));
  }

  @override
  Future<PutAwayOperation> confirmPutAway(PutAwayInput input) {
    return _guard(() => _remote.confirmPutAway(input));
  }

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw mapDioError(error);
    } catch (error) {
      throw ApiError(error.toString(), code: 'INVENTORY_CLIENT_ERROR');
    }
  }
}

final inventoryRepositoryProvider = Provider<InventoryRepository>((ref) {
  return InventoryRepositoryImpl(ref.watch(inventoryRemoteDataSourceProvider));
});
