import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/features/categories/data/category_repository_impl.dart';
import 'package:rigaud_tech_erp/features/categories/domain/category.dart';
import 'package:rigaud_tech_erp/features/categories/domain/category_input.dart';
import 'package:rigaud_tech_erp/features/categories/domain/category_repository.dart';
import 'package:rigaud_tech_erp/features/categories/presentation/category_controller.dart';

void main() {
  test('CategoriesController lista e cria categorias em árvore', () async {
    final repository = _FakeCategoryRepository();
    final container = ProviderContainer(
      overrides: [categoryRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    final initial = await container.read(categoriesControllerProvider.future);
    expect(initial, isEmpty);

    final created = await container
        .read(categoriesControllerProvider.notifier)
        .create(
          const CategoryInput(
            name: 'Bebidas',
            internalCode: 'CAT-001',
            slug: 'bebidas',
            displayOrder: 0,
          ),
        );

    expect(created?.slug, 'bebidas');
    final updatedState = container.read(categoriesControllerProvider).value;
    expect(updatedState?.single.name, 'Bebidas');
  });
}

class _FakeCategoryRepository implements CategoryRepository {
  final List<Category> _items = [];

  @override
  Future<List<Category>> list({
    String? search,
    bool tree = false,
    int page = 1,
    int pageSize = 20,
  }) async {
    if (search == null || search.isEmpty) {
      return _items;
    }
    return _items.where((item) => item.name.contains(search)).toList();
  }

  @override
  Future<Category> get(String id) async {
    return _items.firstWhere((item) => item.id == id);
  }

  @override
  Future<Category> create(CategoryInput input) async {
    final category = Category(
      id: 'category-${_items.length + 1}',
      tenantId: 'tenant-1',
      parentId: input.parentId,
      internalCode: input.internalCode,
      name: input.name,
      slug: input.slug ?? input.name.toLowerCase(),
      description: input.description,
      icon: input.icon,
      color: input.color,
      displayOrder: input.displayOrder,
      status: CategoryStatus.active,
      isActive: true,
      createdAt: DateTime.utc(2026, 7, 31),
      updatedAt: DateTime.utc(2026, 7, 31),
    );
    _items.add(category);
    return category;
  }

  @override
  Future<Category> update(String id, CategoryInput input) async {
    final index = _items.indexWhere((item) => item.id == id);
    final category = await create(input);
    _items[index] = category;
    return category;
  }

  @override
  Future<Category> activate(String id) async => get(id);

  @override
  Future<Category> deactivate(String id) async => get(id);

  @override
  Future<Category> reorder(String id, int displayOrder) async => get(id);

  @override
  Future<Category> delete(String id) async => get(id);
}
