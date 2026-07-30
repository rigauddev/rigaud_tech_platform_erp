import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/product_repository_impl.dart';
import '../domain/product.dart';
import '../domain/product_input.dart';
import '../domain/product_repository.dart';
import '../domain/product_use_cases.dart';

final productsControllerProvider =
    AsyncNotifierProvider<ProductsController, List<Product>>(
      ProductsController.new,
    );

final productDetailsProvider = FutureProvider.family<Product, String>((
  ref,
  id,
) {
  return GetProductUseCase(ref.watch(productRepositoryProvider)).execute(id);
});

class ProductsController extends AsyncNotifier<List<Product>> {
  ProductRepository get _repository => ref.read(productRepositoryProvider);

  @override
  Future<List<Product>> build() {
    return ListProductsUseCase(_repository).execute();
  }

  Future<void> reload({String? search}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListProductsUseCase(_repository).execute(search: search),
    );
  }

  Future<Product?> create(ProductInput input) async {
    final result = await AsyncValue.guard(
      () => CreateProductUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<Product?> updateProduct(String id, ProductInput input) async {
    final result = await AsyncValue.guard(
      () => UpdateProductUseCase(_repository).execute(id, input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(productDetailsProvider(id));
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<void> activate(String id) =>
      _change(id, () => _repository.activate(id));

  Future<void> deactivate(String id) =>
      _change(id, () => _repository.deactivate(id));

  Future<void> changeAvailability(String id, bool available) {
    return _change(id, () => _repository.changeAvailability(id, available));
  }

  Future<void> deleteProduct(String id) =>
      _change(id, () => _repository.delete(id));

  Future<void> _change(String id, Future<Product> Function() action) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
      ref.invalidate(productDetailsProvider(id));
    } else {
      state = AsyncError(result.error!, result.stackTrace!);
    }
  }
}
