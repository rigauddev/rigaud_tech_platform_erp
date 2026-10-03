import 'auth_repository.dart';
import 'mfa.dart';

class LoginUseCase {
  const LoginUseCase(this._repository);

  final AuthRepository _repository;

  Future<AuthLoginResult> execute({
    required String email,
    required String password,
  }) {
    return _repository.login(email: email, password: password);
  }
}
