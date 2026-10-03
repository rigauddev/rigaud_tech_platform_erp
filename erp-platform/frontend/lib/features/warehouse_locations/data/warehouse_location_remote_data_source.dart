import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/warehouse_location.dart';
import '../domain/warehouse_location_input.dart';

class WarehouseLocationRemoteDataSource {
  const WarehouseLocationRemoteDataSource(this._dio);

  final Dio _dio;

  Future<List<WarehouseLocation>> list({
    String? warehouseId,
    String? zoneId,
    String? search,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/warehouse-locations',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (warehouseId case final String id) 'warehouse_id': id,
        if (zoneId case final String id) 'zone_id': id,
        if (search case final String value) 'search': value,
        if (isActive case final bool active) 'is_active': active,
      },
    );
    return apiDataList(response.data)
        .map((item) => WarehouseLocation.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<WarehouseLocation> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/warehouse-locations/$id',
    );
    return WarehouseLocation.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseLocation> create(WarehouseLocationInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/warehouse-locations',
      data: input.toJson(),
    );
    return WarehouseLocation.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseLocation> update(
    String id,
    WarehouseLocationInput input,
  ) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/api/v1/warehouse-locations/$id',
      data: input.toJson(),
    );
    return WarehouseLocation.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseLocation> activate(String id) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/warehouse-locations/$id/activate',
    );
    return WarehouseLocation.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseLocation> deactivate(String id) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/warehouse-locations/$id/deactivate',
    );
    return WarehouseLocation.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseLocation> reorder(String id, int sortOrder) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/warehouse-locations/$id/reorder',
      data: {'sort_order': sortOrder},
    );
    return WarehouseLocation.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseLocation> delete(String id) async {
    final response = await _dio.delete<Map<String, dynamic>>(
      '/api/v1/warehouse-locations/$id',
    );
    return WarehouseLocation.fromJson(apiDataObject(response.data));
  }
}

final warehouseLocationRemoteDataSourceProvider =
    Provider<WarehouseLocationRemoteDataSource>((ref) {
      return WarehouseLocationRemoteDataSource(ref.watch(dioProvider));
    });
