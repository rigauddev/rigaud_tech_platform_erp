import 'auth_tokens.dart';
import 'auth_user.dart';
import 'access_context.dart';
import 'mfa.dart';

abstract interface class AuthRepository {
  Future<AuthLoginResult> login({
    required String email,
    required String password,
  });

  Future<AuthTokens> verifyMfa({
    required String challengeId,
    required String method,
    required String code,
  });

  Future<AuthTokens> refresh(String refreshToken);

  Future<void> logout(String refreshToken);

  Future<AuthUser> me();

  Future<ContextOptions> contextOptions();

  Future<ContextAccessToken> switchContext({
    required String tenantId,
    String? branchId,
  });
}
