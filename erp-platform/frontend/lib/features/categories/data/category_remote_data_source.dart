import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/category.dart';
import '../domain/category_input.dart';

class CategoryRemoteDataSource {
  const CategoryRemoteDataSource(this._dio);

  final Dio _dio;

  Future<List<Category>> list({
    String? search,
    bool tree = false,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/categories',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        'tree': tree,
        if (search != null && search.trim().isNotEmpty) 'search': search,
      },
    );
    final items = apiDataList(response.data);
    return items
        .map((item) => Category.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Category> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/categories/$id',
    );
    return Category.fromJson(apiDataObject(response.data));
  }

  Future<Category> create(CategoryInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/categories',
      data: input.toJson(),
    );
    return Category.fromJson(apiDataObject(response.data));
  }

  Future<Category> update(String id, CategoryInput input) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/api/v1/categories/$id',
      data: input.toJson(),
    );
    return Category.fromJson(apiDataObject(response.data));
  }

  Future<Category> activate(String id) => _statusAction(id, 'activate');

  Future<Category> deactivate(String id) => _statusAction(id, 'deactivate');

  Future<Category> reorder(String id, int displayOrder) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/categories/$id/reorder',
      data: {'display_order': displayOrder},
    );
    return Category.fromJson(apiDataObject(response.data));
  }

  Future<Category> delete(String id) async {
    final response = await _dio.delete<Map<String, dynamic>>(
      '/api/v1/categories/$id',
    );
    return Category.fromJson(apiDataObject(response.data));
  }

  Future<Category> _statusAction(String id, String action) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/categories/$id/$action',
    );
    return Category.fromJson(apiDataObject(response.data));
  }
}

final categoryRemoteDataSourceProvider = Provider<CategoryRemoteDataSource>((
  ref,
) {
  return CategoryRemoteDataSource(ref.watch(dioProvider));
});
