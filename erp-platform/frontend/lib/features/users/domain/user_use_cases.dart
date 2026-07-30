import 'user.dart';
import 'user_input.dart';
import 'user_repository.dart';

class ListUsersUseCase {
  const ListUsersUseCase(this._repository);

  final UserRepository _repository;

  Future<UserPage> execute({int page = 1, String? search}) {
    return _repository.list(page: page, search: search);
  }
}

class GetUserUseCase {
  const GetUserUseCase(this._repository);

  final UserRepository _repository;

  Future<UserProfile> execute(String id) => _repository.get(id);
}

class GetMyUserUseCase {
  const GetMyUserUseCase(this._repository);

  final UserRepository _repository;

  Future<UserProfile> execute() => _repository.me();
}

class CreateUserUseCase {
  const CreateUserUseCase(this._repository);

  final UserRepository _repository;

  Future<UserProfile> execute(UserCreateInput input) =>
      _repository.create(input);
}

class UpdateUserUseCase {
  const UpdateUserUseCase(this._repository);

  final UserRepository _repository;

  Future<UserProfile> execute(String id, UserUpdateInput input) =>
      _repository.update(id, input);
}
