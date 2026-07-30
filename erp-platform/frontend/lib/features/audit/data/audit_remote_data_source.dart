import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/audit_event.dart';

class AuditRemoteDataSource {
  const AuditRemoteDataSource(this._dio);

  final Dio _dio;

  Future<AuditEventPage> list({
    int page = 1,
    String? module,
    String? requestId,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/audit/events',
      queryParameters: {
        'page': page,
        if (module != null && module.isNotEmpty) 'module': module,
        if (requestId != null && requestId.isNotEmpty) 'request_id': requestId,
      },
    );
    final envelope = ApiEnvelope.fromJson(response.data ?? {});
    return AuditEventPage(
      items: apiDataList(response.data)
          .map((item) => AuditEvent.fromJson(item as Map<String, dynamic>))
          .toList(),
      total: envelope.meta?.total ?? 0,
      page: envelope.meta?.page ?? page,
      pageSize: envelope.meta?.pageSize ?? 20,
    );
  }

  Future<AuditEvent> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/audit/events/$id',
    );
    return AuditEvent.fromJson(apiDataObject(response.data));
  }
}

final auditRemoteDataSourceProvider = Provider<AuditRemoteDataSource>((ref) {
  return AuditRemoteDataSource(ref.watch(dioProvider));
});
