import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/storage/secure_storage.dart';
import '../data/auth_repository_impl.dart';
import '../domain/auth_repository.dart';
import '../domain/auth_state.dart';
import '../domain/login_use_case.dart';

final authControllerProvider = AsyncNotifierProvider<AuthController, AuthState>(
  AuthController.new,
);

class AuthController extends AsyncNotifier<AuthState> {
  AuthRepository get _repository => ref.read(authRepositoryProvider);

  SecureStorage get _storage => ref.read(secureStorageProvider);

  @override
  Future<AuthState> build() async {
    final token = await _storage.readAccessToken();
    if (token == null || token.isEmpty) {
      return const AuthState.unauthenticated();
    }

    try {
      final user = await _repository.me();
      return AuthState.authenticated(user);
    } catch (_) {
      await _storage.clearTokens();
      return const AuthState.unauthenticated();
    }
  }

  Future<void> login({
    required String tenant,
    required String email,
    required String password,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final result = await LoginUseCase(
        _repository,
      ).execute(tenant: tenant, email: email, password: password);
      if (result.requiresMfa) {
        return AuthState.mfaRequired(result.mfaChallenge);
      }
      final user = await _repository.me();
      return AuthState.authenticated(user);
    });
  }

  Future<void> verifyMfa({
    required String challengeId,
    required String method,
    required String code,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repository.verifyMfa(
        challengeId: challengeId,
        method: method,
        code: code,
      );
      final user = await _repository.me();
      return AuthState.authenticated(user);
    });
  }

  void cancelMfa() {
    state = const AsyncData(AuthState.unauthenticated());
  }

  Future<void> switchContext({
    required String tenantId,
    String? branchId,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repository.switchContext(tenantId: tenantId, branchId: branchId);
      final user = await _repository.me();
      return AuthState.authenticated(user);
    });
  }

  Future<void> logout() async {
    final refreshToken = await _storage.readRefreshToken();
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      if (refreshToken != null && refreshToken.isNotEmpty) {
        await _repository.logout(refreshToken);
      } else {
        await _storage.clearTokens();
      }
      return const AuthState.unauthenticated();
    });
  }
}
