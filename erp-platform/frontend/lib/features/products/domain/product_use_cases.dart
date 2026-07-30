import 'product.dart';
import 'product_input.dart';
import 'product_repository.dart';

class ListProductsUseCase {
  const ListProductsUseCase(this._repository);

  final ProductRepository _repository;

  Future<List<Product>> execute({String? search}) {
    return _repository.list(search: search);
  }
}

class GetProductUseCase {
  const GetProductUseCase(this._repository);

  final ProductRepository _repository;

  Future<Product> execute(String id) => _repository.get(id);
}

class CreateProductUseCase {
  const CreateProductUseCase(this._repository);

  final ProductRepository _repository;

  Future<Product> execute(ProductInput input) => _repository.create(input);
}

class UpdateProductUseCase {
  const UpdateProductUseCase(this._repository);

  final ProductRepository _repository;

  Future<Product> execute(String id, ProductInput input) {
    return _repository.update(id, input);
  }
}
