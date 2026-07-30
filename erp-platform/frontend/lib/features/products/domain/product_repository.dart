import 'product.dart';
import 'product_input.dart';

abstract interface class ProductRepository {
  Future<List<Product>> list({String? search, int page = 1, int pageSize = 20});

  Future<Product> get(String id);

  Future<Product> create(ProductInput input);

  Future<Product> update(String id, ProductInput input);

  Future<Product> activate(String id);

  Future<Product> deactivate(String id);

  Future<Product> changeAvailability(String id, bool available);

  Future<Product> delete(String id);
}
