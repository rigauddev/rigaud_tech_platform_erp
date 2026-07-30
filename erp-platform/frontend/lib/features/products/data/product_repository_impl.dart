import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_error.dart';
import '../domain/product.dart';
import '../domain/product_input.dart';
import '../domain/product_repository.dart';
import 'product_remote_data_source.dart';

class ProductRepositoryImpl implements ProductRepository {
  const ProductRepositoryImpl(this._remote);

  final ProductRemoteDataSource _remote;

  @override
  Future<List<Product>> list({
    String? search,
    int page = 1,
    int pageSize = 20,
  }) {
    return _guard(
      () => _remote.list(search: search, page: page, pageSize: pageSize),
    );
  }

  @override
  Future<Product> get(String id) => _guard(() => _remote.get(id));

  @override
  Future<Product> create(ProductInput input) =>
      _guard(() => _remote.create(input));

  @override
  Future<Product> update(String id, ProductInput input) {
    return _guard(() => _remote.update(id, input));
  }

  @override
  Future<Product> activate(String id) => _guard(() => _remote.activate(id));

  @override
  Future<Product> deactivate(String id) => _guard(() => _remote.deactivate(id));

  @override
  Future<Product> changeAvailability(String id, bool available) {
    return _guard(() => _remote.changeAvailability(id, available));
  }

  @override
  Future<Product> delete(String id) => _guard(() => _remote.delete(id));

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw mapDioError(error);
    } catch (error) {
      throw ApiError(error.toString(), code: 'PRODUCTS_CLIENT_ERROR');
    }
  }
}

final productRepositoryProvider = Provider<ProductRepository>((ref) {
  return ProductRepositoryImpl(ref.watch(productRemoteDataSourceProvider));
});
