import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/category_repository_impl.dart';
import '../domain/category.dart';
import '../domain/category_input.dart';
import '../domain/category_repository.dart';
import '../domain/category_use_cases.dart';

final categoriesControllerProvider =
    AsyncNotifierProvider<CategoriesController, List<Category>>(
      CategoriesController.new,
    );

final categoryDetailsProvider = FutureProvider.family<Category, String>((
  ref,
  id,
) {
  return GetCategoryUseCase(ref.watch(categoryRepositoryProvider)).execute(id);
});

class CategoriesController extends AsyncNotifier<List<Category>> {
  CategoryRepository get _repository => ref.read(categoryRepositoryProvider);

  @override
  Future<List<Category>> build() {
    return ListCategoriesUseCase(_repository).execute(tree: true);
  }

  Future<void> reload({String? search}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListCategoriesUseCase(
        _repository,
      ).execute(search: search, tree: true),
    );
  }

  Future<Category?> create(CategoryInput input) async {
    final result = await AsyncValue.guard(
      () => CreateCategoryUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<Category?> updateCategory(String id, CategoryInput input) async {
    final result = await AsyncValue.guard(
      () => UpdateCategoryUseCase(_repository).execute(id, input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(categoryDetailsProvider(id));
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<void> activate(String id) =>
      _change(id, () => _repository.activate(id));

  Future<void> deactivate(String id) =>
      _change(id, () => _repository.deactivate(id));

  Future<void> deleteCategory(String id) =>
      _change(id, () => _repository.delete(id));

  Future<void> _change(String id, Future<Category> Function() action) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
      ref.invalidate(categoryDetailsProvider(id));
    } else {
      state = AsyncError(result.error!, result.stackTrace!);
    }
  }
}
