import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/storage/secure_storage.dart';
import '../domain/auth_repository.dart';
import '../domain/auth_tokens.dart';
import '../domain/auth_user.dart';
import '../domain/mfa.dart';
import 'auth_remote_data_source.dart';

class AuthRepositoryImpl implements AuthRepository {
  const AuthRepositoryImpl({
    required AuthRemoteDataSource remoteDataSource,
    required SecureStorage secureStorage,
  }) : _remoteDataSource = remoteDataSource,
       _secureStorage = secureStorage;

  final AuthRemoteDataSource _remoteDataSource;
  final SecureStorage _secureStorage;

  @override
  Future<AuthLoginResult> login({
    required String tenant,
    required String email,
    required String password,
  }) async {
    try {
      final result = await _remoteDataSource.login(
        tenant: tenant,
        email: email,
        password: password,
      );
      final tokens = result.tokens;
      if (tokens != null) {
        await _secureStorage.writeTokens(
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
        );
      }
      return result;
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }

  @override
  Future<AuthTokens> verifyMfa({
    required String challengeId,
    required String method,
    required String code,
  }) async {
    try {
      final tokens = await _remoteDataSource.verifyMfa(
        challengeId: challengeId,
        method: method,
        code: code,
      );
      await _secureStorage.writeTokens(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      );
      return tokens;
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }

  @override
  Future<AuthTokens> refresh(String refreshToken) async {
    try {
      final tokens = await _remoteDataSource.refresh(refreshToken);
      await _secureStorage.writeTokens(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      );
      return tokens;
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }

  @override
  Future<void> logout(String refreshToken) async {
    try {
      await _remoteDataSource.logout(refreshToken);
    } on DioException catch (error) {
      throw mapDioError(error);
    } finally {
      await _secureStorage.clearTokens();
    }
  }

  @override
  Future<AuthUser> me() async {
    try {
      return _remoteDataSource.me();
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl(
    remoteDataSource: ref.watch(authRemoteDataSourceProvider),
    secureStorage: ref.watch(secureStorageProvider),
  );
});
