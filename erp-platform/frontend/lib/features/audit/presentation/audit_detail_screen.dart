import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_spacing.dart';
import '../../../shared/layouts/app_scaffold.dart';
import 'audit_controller.dart';

class AuditDetailScreen extends ConsumerWidget {
  const AuditDetailScreen({required this.eventId, super.key});

  final String eventId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final event = ref.watch(auditEventProvider(eventId));
    return AppScaffold(
      title: 'Evento de auditoria',
      selectedIndex: 3,
      body: event.when(
        data: (item) => ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            _row('Evento', item.eventName),
            _row('Módulo', item.module),
            _row('Ação', item.action),
            _row(
              'Entidade',
              '${item.entityType ?? '-'} ${item.entityId ?? ''}',
            ),
            _row('Tenant', item.tenantId ?? '-'),
            _row('Ator', item.actorUserId ?? '-'),
            _row('Data', item.occurredAt?.toLocal().toString() ?? '-'),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Request ID'),
              subtitle: Text(item.requestId ?? '-'),
              trailing: IconButton(
                tooltip: 'Copiar',
                icon: const Icon(Icons.copy),
                onPressed: item.requestId == null
                    ? null
                    : () => Clipboard.setData(
                        ClipboardData(text: item.requestId!),
                      ),
              ),
            ),
          ],
        ),
        error: (error, stackTrace) =>
            const Center(child: Text('Evento não encontrado.')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 4),
          Text(value),
        ],
      ),
    );
  }
}
