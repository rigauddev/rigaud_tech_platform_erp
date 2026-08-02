import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/warehouse_zone.dart';
import '../domain/warehouse_zone_input.dart';

class WarehouseZoneRemoteDataSource {
  const WarehouseZoneRemoteDataSource(this._dio);

  final Dio _dio;

  Future<List<WarehouseZone>> list({
    String? warehouseId,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/warehouse-zones',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (warehouseId case final String id) 'warehouse_id': id,
        if (isActive case final bool active) 'is_active': active,
      },
    );
    return apiDataList(response.data)
        .map((item) => WarehouseZone.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<WarehouseZone> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/warehouse-zones/$id',
    );
    return WarehouseZone.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseZone> create(WarehouseZoneInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/warehouse-zones',
      data: input.toJson(),
    );
    return WarehouseZone.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseZone> update(String id, WarehouseZoneInput input) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/api/v1/warehouse-zones/$id',
      data: input.toJson(),
    );
    return WarehouseZone.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseZone> reorder(String id, int sortOrder) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/warehouse-zones/$id/reorder',
      data: {'sort_order': sortOrder},
    );
    return WarehouseZone.fromJson(apiDataObject(response.data));
  }

  Future<WarehouseZone> delete(String id) async {
    final response = await _dio.delete<Map<String, dynamic>>(
      '/api/v1/warehouse-zones/$id',
    );
    return WarehouseZone.fromJson(apiDataObject(response.data));
  }
}

final warehouseZoneRemoteDataSourceProvider =
    Provider<WarehouseZoneRemoteDataSource>((ref) {
      return WarehouseZoneRemoteDataSource(ref.watch(dioProvider));
    });
