class AuditEvent {
  const AuditEvent({
    required this.id,
    required this.eventName,
    required this.module,
    required this.action,
    this.entityType,
    this.entityId,
    this.tenantId,
    this.actorUserId,
    this.requestId,
    this.occurredAt,
  });

  final String id;
  final String eventName;
  final String module;
  final String action;
  final String? entityType;
  final String? entityId;
  final String? tenantId;
  final String? actorUserId;
  final String? requestId;
  final DateTime? occurredAt;

  factory AuditEvent.fromJson(Map<String, dynamic> json) {
    return AuditEvent(
      id: json['id'] as String? ?? '',
      eventName: json['event_name'] as String? ?? '',
      module: json['module'] as String? ?? '',
      action: json['action'] as String? ?? '',
      entityType: json['entity_type'] as String?,
      entityId: json['entity_id'] as String?,
      tenantId: json['tenant_id'] as String?,
      actorUserId: json['actor_user_id'] as String?,
      requestId: json['request_id'] as String?,
      occurredAt: DateTime.tryParse(json['occurred_at'] as String? ?? ''),
    );
  }
}

class AuditEventPage {
  const AuditEventPage({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  final List<AuditEvent> items;
  final int total;
  final int page;
  final int pageSize;
}
