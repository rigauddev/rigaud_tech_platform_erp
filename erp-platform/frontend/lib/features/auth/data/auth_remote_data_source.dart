import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/auth_tokens.dart';
import '../domain/auth_user.dart';
import '../domain/mfa.dart';

class AuthRemoteDataSource {
  const AuthRemoteDataSource(this._dio);

  final Dio _dio;

  Future<AuthLoginResult> login({
    required String tenant,
    required String email,
    required String password,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/auth/login',
      data: {'tenant': tenant, 'email': email, 'password': password},
    );
    final envelope = ApiEnvelope.fromJson(response.data ?? {});
    final data = apiDataObject(response.data);
    if (envelope.code == 'AUTH_MFA_REQUIRED') {
      return AuthLoginResult.mfaRequired(MfaChallenge.fromJson(data));
    }
    return AuthLoginResult.tokens(_tokensFromJson(data));
  }

  Future<AuthTokens> verifyMfa({
    required String challengeId,
    required String method,
    required String code,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/auth/mfa/verify',
      data: {'challenge_id': challengeId, 'method': method, 'code': code},
    );
    return _tokensFromJson(apiDataObject(response.data));
  }

  Future<AuthTokens> refresh(String refreshToken) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/auth/refresh',
      data: {'refresh_token': refreshToken},
    );
    return _tokensFromJson(apiDataObject(response.data));
  }

  Future<void> logout(String refreshToken) async {
    await _dio.post<void>(
      '/api/v1/auth/logout',
      data: {'refresh_token': refreshToken},
    );
  }

  Future<AuthUser> me() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/auth/me');
    final data = apiDataObject(response.data);
    return AuthUser(
      id: data['id'] as String? ?? '',
      tenantId: data['tenant_id'] as String? ?? '',
      email: data['email'] as String? ?? '',
      isActive: data['is_active'] as bool? ?? false,
      isSuperuser: data['is_superuser'] as bool? ?? false,
    );
  }

  AuthTokens _tokensFromJson(Map<String, dynamic> data) {
    return AuthTokens(
      accessToken: data['access_token'] as String? ?? '',
      refreshToken: data['refresh_token'] as String? ?? '',
      tokenType: data['token_type'] as String? ?? 'bearer',
      expiresIn: data['expires_in'] as int? ?? 0,
    );
  }
}

final authRemoteDataSourceProvider = Provider<AuthRemoteDataSource>((ref) {
  return AuthRemoteDataSource(ref.watch(dioProvider));
});
