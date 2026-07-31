import 'category.dart';
import 'category_input.dart';

abstract interface class CategoryRepository {
  Future<List<Category>> list({
    String? search,
    bool tree = false,
    int page = 1,
    int pageSize = 20,
  });

  Future<Category> get(String id);

  Future<Category> create(CategoryInput input);

  Future<Category> update(String id, CategoryInput input);

  Future<Category> activate(String id);

  Future<Category> deactivate(String id);

  Future<Category> reorder(String id, int displayOrder);

  Future<Category> delete(String id);
}
