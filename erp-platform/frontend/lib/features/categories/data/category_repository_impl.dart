import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/category.dart';
import '../domain/category_input.dart';
import '../domain/category_repository.dart';
import 'category_remote_data_source.dart';

class CategoryRepositoryImpl implements CategoryRepository {
  const CategoryRepositoryImpl(this._remote);

  final CategoryRemoteDataSource _remote;

  @override
  Future<List<Category>> list({
    String? search,
    bool tree = false,
    int page = 1,
    int pageSize = 20,
  }) {
    return _remote.list(
      search: search,
      tree: tree,
      page: page,
      pageSize: pageSize,
    );
  }

  @override
  Future<Category> get(String id) => _remote.get(id);

  @override
  Future<Category> create(CategoryInput input) => _remote.create(input);

  @override
  Future<Category> update(String id, CategoryInput input) {
    return _remote.update(id, input);
  }

  @override
  Future<Category> activate(String id) => _remote.activate(id);

  @override
  Future<Category> deactivate(String id) => _remote.deactivate(id);

  @override
  Future<Category> reorder(String id, int displayOrder) {
    return _remote.reorder(id, displayOrder);
  }

  @override
  Future<Category> delete(String id) => _remote.delete(id);
}

final categoryRepositoryProvider = Provider<CategoryRepository>((ref) {
  return CategoryRepositoryImpl(ref.watch(categoryRemoteDataSourceProvider));
});
