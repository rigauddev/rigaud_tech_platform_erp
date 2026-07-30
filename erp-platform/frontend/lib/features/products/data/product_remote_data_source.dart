import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/product.dart';
import '../domain/product_input.dart';

class ProductRemoteDataSource {
  const ProductRemoteDataSource(this._dio);

  final Dio _dio;

  Future<List<Product>> list({
    String? search,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/products',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (search != null && search.trim().isNotEmpty) 'search': search,
      },
    );
    final items = apiDataList(response.data);
    return items
        .map((item) => Product.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Product> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/products/$id',
    );
    return Product.fromJson(apiDataObject(response.data));
  }

  Future<Product> create(ProductInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/products',
      data: input.toJson(),
    );
    return Product.fromJson(apiDataObject(response.data));
  }

  Future<Product> update(String id, ProductInput input) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/api/v1/products/$id',
      data: input.toJson(),
    );
    return Product.fromJson(apiDataObject(response.data));
  }

  Future<Product> activate(String id) => _statusAction(id, 'activate');

  Future<Product> deactivate(String id) => _statusAction(id, 'deactivate');

  Future<Product> changeAvailability(String id, bool available) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/products/$id/availability',
      data: {'is_available_for_sale': available},
    );
    return Product.fromJson(apiDataObject(response.data));
  }

  Future<Product> delete(String id) async {
    final response = await _dio.delete<Map<String, dynamic>>(
      '/api/v1/products/$id',
    );
    return Product.fromJson(apiDataObject(response.data));
  }

  Future<Product> _statusAction(String id, String action) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/products/$id/$action',
    );
    return Product.fromJson(apiDataObject(response.data));
  }
}

final productRemoteDataSourceProvider = Provider<ProductRemoteDataSource>((
  ref,
) {
  return ProductRemoteDataSource(ref.watch(dioProvider));
});
