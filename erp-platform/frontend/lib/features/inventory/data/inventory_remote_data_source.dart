import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/inventory.dart';
import '../domain/inventory_input.dart';

class InventoryRemoteDataSource {
  const InventoryRemoteDataSource(this._dio);

  final Dio _dio;

  Future<List<InventoryBalance>> listBalances({
    String? productId,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/inventory/balances',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (productId != null && productId.trim().isNotEmpty)
          'product_id': productId,
      },
    );
    return apiDataList(response.data)
        .map((item) => InventoryBalance.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<InventoryMovement>> listMovements({
    String? productId,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/inventory/movements',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (productId != null && productId.trim().isNotEmpty)
          'product_id': productId,
      },
    );
    return apiDataList(response.data)
        .map((item) => InventoryMovement.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<InventoryOperation> createAdjustment(
    InventoryAdjustmentInput input,
  ) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/inventory/adjustments',
      data: input.toJson(),
    );
    return InventoryOperation.fromJson(apiDataObject(response.data));
  }

  Future<InventoryOperation> createReservation(
    InventoryReservationInput input,
  ) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/inventory/reservations',
      data: input.toJson(),
    );
    return InventoryOperation.fromJson(apiDataObject(response.data));
  }

  Future<PutAwayOperation> confirmPutAway(PutAwayInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/inventory/putaway',
      data: input.toJson(),
    );
    return PutAwayOperation.fromJson(apiDataObject(response.data));
  }
}

final inventoryRemoteDataSourceProvider = Provider<InventoryRemoteDataSource>((
  ref,
) {
  return InventoryRemoteDataSource(ref.watch(dioProvider));
});
