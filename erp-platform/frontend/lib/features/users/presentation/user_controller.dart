import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/user_repository_impl.dart';
import '../domain/user.dart';
import '../domain/user_input.dart';
import '../domain/user_repository.dart';
import '../domain/user_use_cases.dart';

final usersControllerProvider =
    AsyncNotifierProvider<UsersController, UserPage>(UsersController.new);

final userDetailsProvider = FutureProvider.family<UserProfile, String>((
  ref,
  id,
) {
  return GetUserUseCase(ref.watch(userRepositoryProvider)).execute(id);
});

final currentUserProfileProvider = FutureProvider<UserProfile>((ref) {
  return GetMyUserUseCase(ref.watch(userRepositoryProvider)).execute();
});

class UsersController extends AsyncNotifier<UserPage> {
  UserRepository get _repository => ref.read(userRepositoryProvider);

  int _page = 1;
  String? _search;

  @override
  Future<UserPage> build() {
    return ListUsersUseCase(_repository).execute();
  }

  Future<void> reload({int? page, String? search}) async {
    _page = page ?? _page;
    _search = search ?? _search;
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListUsersUseCase(_repository).execute(page: _page, search: _search),
    );
  }

  Future<UserProfile?> create(UserCreateInput input) async {
    final result = await AsyncValue.guard(
      () => CreateUserUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<UserProfile?> updateUser(String id, UserUpdateInput input) async {
    final result = await AsyncValue.guard(
      () => UpdateUserUseCase(_repository).execute(id, input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(userDetailsProvider(id));
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<void> activate(String id) =>
      _changeStatus(id, () => _repository.activate(id));

  Future<void> deactivate(String id) =>
      _changeStatus(id, () => _repository.deactivate(id));

  Future<void> block(String id) =>
      _changeStatus(id, () => _repository.block(id));

  Future<void> unblock(String id) =>
      _changeStatus(id, () => _repository.unblock(id));

  Future<void> _changeStatus(
    String id,
    Future<UserProfile> Function() action,
  ) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
      ref.invalidate(userDetailsProvider(id));
    } else {
      state = AsyncError(result.error!, result.stackTrace!);
    }
  }
}
