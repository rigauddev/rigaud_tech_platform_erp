import 'audit_event.dart';

abstract interface class AuditRepository {
  Future<AuditEventPage> list({
    int page = 1,
    String? module,
    String? requestId,
  });

  Future<AuditEvent> get(String id);
}
