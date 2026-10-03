import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/warehouse.dart';
import '../domain/warehouse_input.dart';

class WarehouseRemoteDataSource {
  const WarehouseRemoteDataSource(this._dio);

  final Dio _dio;

  Future<List<Warehouse>> list({
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/warehouses',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (isActive case final bool active) 'is_active': active,
      },
    );
    return apiDataList(
      response.data,
    ).map((item) => Warehouse.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<Warehouse> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/warehouses/$id',
    );
    return Warehouse.fromJson(apiDataObject(response.data));
  }

  Future<Warehouse> create(WarehouseInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/warehouses',
      data: input.toJson(),
    );
    return Warehouse.fromJson(apiDataObject(response.data));
  }

  Future<Warehouse> update(String id, WarehouseInput input) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/api/v1/warehouses/$id',
      data: input.toJson(),
    );
    return Warehouse.fromJson(apiDataObject(response.data));
  }

  Future<Warehouse> setDefault(String id) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/warehouses/$id/default',
    );
    return Warehouse.fromJson(apiDataObject(response.data));
  }

  Future<Warehouse> delete(String id) async {
    final response = await _dio.delete<Map<String, dynamic>>(
      '/api/v1/warehouses/$id',
    );
    return Warehouse.fromJson(apiDataObject(response.data));
  }
}

final warehouseRemoteDataSourceProvider = Provider<WarehouseRemoteDataSource>((
  ref,
) {
  return WarehouseRemoteDataSource(ref.watch(dioProvider));
});
