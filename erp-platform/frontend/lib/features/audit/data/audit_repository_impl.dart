import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../domain/audit_event.dart';
import '../domain/audit_repository.dart';
import 'audit_remote_data_source.dart';

class AuditRepositoryImpl implements AuditRepository {
  const AuditRepositoryImpl(this._remote);

  final AuditRemoteDataSource _remote;

  @override
  Future<AuditEventPage> list({
    int page = 1,
    String? module,
    String? requestId,
  }) {
    return _guard(
      () => _remote.list(page: page, module: module, requestId: requestId),
    );
  }

  @override
  Future<AuditEvent> get(String id) => _guard(() => _remote.get(id));

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }
}

final auditRepositoryProvider = Provider<AuditRepository>((ref) {
  return AuditRepositoryImpl(ref.watch(auditRemoteDataSourceProvider));
});
