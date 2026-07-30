import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/features/products/data/product_repository_impl.dart';
import 'package:rigaud_tech_erp/features/products/domain/product.dart';
import 'package:rigaud_tech_erp/features/products/domain/product_input.dart';
import 'package:rigaud_tech_erp/features/products/domain/product_repository.dart';
import 'package:rigaud_tech_erp/features/products/presentation/product_controller.dart';

void main() {
  test('ProductsController lista e cria produtos', () async {
    final repository = _FakeProductRepository();
    final container = ProviderContainer(
      overrides: [productRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    final initial = await container.read(productsControllerProvider.future);
    expect(initial, isEmpty);

    final created = await container
        .read(productsControllerProvider.notifier)
        .create(
          const ProductInput(
            name: 'Hamburguer',
            internalCode: 'PRD-001',
            productType: ProductType.preparedItem,
            unitOfMeasure: UnitOfMeasure.unit,
            salePrice: '29.90',
            costPrice: '12.40',
            isAvailableForSale: true,
          ),
        );

    expect(created?.internalCode, 'PRD-001');
    final updatedState = container.read(productsControllerProvider).value;
    expect(updatedState?.single.name, 'Hamburguer');
  });
}

class _FakeProductRepository implements ProductRepository {
  final List<Product> _items = [];

  @override
  Future<List<Product>> list({
    String? search,
    int page = 1,
    int pageSize = 20,
  }) async {
    if (search == null || search.isEmpty) {
      return _items;
    }
    return _items.where((item) => item.name.contains(search)).toList();
  }

  @override
  Future<Product> get(String id) async {
    return _items.firstWhere((item) => item.id == id);
  }

  @override
  Future<Product> create(ProductInput input) async {
    final product = Product(
      id: 'product-${_items.length + 1}',
      tenantId: 'tenant-1',
      name: input.name,
      description: input.description,
      internalCode: input.internalCode,
      barcode: input.barcode,
      productType: input.productType,
      unitOfMeasure: input.unitOfMeasure,
      salePrice: input.salePrice,
      costPrice: input.costPrice,
      mainImageUrl: input.mainImageUrl,
      isActive: true,
      isAvailableForSale: input.isAvailableForSale,
      createdAt: DateTime.utc(2026, 7, 30),
      updatedAt: DateTime.utc(2026, 7, 30),
    );
    _items.add(product);
    return product;
  }

  @override
  Future<Product> update(String id, ProductInput input) async {
    final index = _items.indexWhere((item) => item.id == id);
    final product = await create(input);
    _items[index] = product;
    return product;
  }

  @override
  Future<Product> activate(String id) async => get(id);

  @override
  Future<Product> deactivate(String id) async => get(id);

  @override
  Future<Product> changeAvailability(String id, bool available) async =>
      get(id);

  @override
  Future<Product> delete(String id) async => get(id);
}
