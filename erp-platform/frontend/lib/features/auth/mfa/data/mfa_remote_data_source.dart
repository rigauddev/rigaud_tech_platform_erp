import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/api/api_client.dart';
import '../../../../core/api/api_response.dart';
import '../../domain/mfa.dart';

class MfaRemoteDataSource {
  const MfaRemoteDataSource(this._dio);

  final Dio _dio;

  Future<MfaStatus> status() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/auth/mfa/status',
    );
    return MfaStatus.fromJson(apiDataObject(response.data));
  }

  Future<TotpSetup> setupTotp() async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/auth/mfa/totp/setup',
    );
    return TotpSetup.fromJson(apiDataObject(response.data));
  }

  Future<List<String>> confirmTotp(String code) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/auth/mfa/totp/confirm',
      data: {'code': code},
    );
    final data = apiDataObject(response.data);
    return (data['codes'] as List<dynamic>? ?? const []).cast<String>();
  }

  Future<List<String>> regenerateRecoveryCodes() async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/auth/mfa/recovery-codes/regenerate',
    );
    return (apiDataObject(response.data)['codes'] as List<dynamic>? ?? const [])
        .cast<String>();
  }

  Future<void> disable(String currentPassword) async {
    await _dio.post<void>(
      '/api/v1/auth/mfa/disable',
      data: {'current_password': currentPassword},
    );
  }
}

final mfaRemoteDataSourceProvider = Provider<MfaRemoteDataSource>((ref) {
  return MfaRemoteDataSource(ref.watch(dioProvider));
});
