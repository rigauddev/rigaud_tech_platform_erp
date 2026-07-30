import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/api/api_client.dart';
import '../../domain/mfa.dart';
import '../domain/mfa_repository.dart';
import 'mfa_remote_data_source.dart';

class MfaRepositoryImpl implements MfaRepository {
  const MfaRepositoryImpl(this._remote);

  final MfaRemoteDataSource _remote;

  @override
  Future<MfaStatus> status() async {
    try {
      return _remote.status();
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }

  @override
  Future<TotpSetup> setupTotp() async {
    try {
      return _remote.setupTotp();
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }

  @override
  Future<List<String>> confirmTotp(String code) async {
    try {
      return _remote.confirmTotp(code);
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }

  @override
  Future<List<String>> regenerateRecoveryCodes() async {
    try {
      return _remote.regenerateRecoveryCodes();
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }

  @override
  Future<void> disable(String currentPassword) async {
    try {
      await _remote.disable(currentPassword);
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }
}

final mfaRepositoryProvider = Provider<MfaRepository>((ref) {
  return MfaRepositoryImpl(ref.watch(mfaRemoteDataSourceProvider));
});
