import 'category.dart';
import 'category_input.dart';
import 'category_repository.dart';

class ListCategoriesUseCase {
  const ListCategoriesUseCase(this._repository);

  final CategoryRepository _repository;

  Future<List<Category>> execute({String? search, bool tree = false}) {
    return _repository.list(search: search, tree: tree);
  }
}

class GetCategoryUseCase {
  const GetCategoryUseCase(this._repository);

  final CategoryRepository _repository;

  Future<Category> execute(String id) => _repository.get(id);
}

class CreateCategoryUseCase {
  const CreateCategoryUseCase(this._repository);

  final CategoryRepository _repository;

  Future<Category> execute(CategoryInput input) => _repository.create(input);
}

class UpdateCategoryUseCase {
  const UpdateCategoryUseCase(this._repository);

  final CategoryRepository _repository;

  Future<Category> execute(String id, CategoryInput input) {
    return _repository.update(id, input);
  }
}
