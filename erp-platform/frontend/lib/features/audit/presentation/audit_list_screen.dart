import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/audit_event.dart';
import 'audit_controller.dart';

class AuditListScreen extends ConsumerStatefulWidget {
  const AuditListScreen({super.key});

  @override
  ConsumerState<AuditListScreen> createState() => _AuditListScreenState();
}

class _AuditListScreenState extends ConsumerState<AuditListScreen> {
  final _module = TextEditingController();
  final _requestId = TextEditingController();

  @override
  void dispose() {
    _module.dispose();
    _requestId.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final page = ref.watch(auditControllerProvider);
    return AppScaffold(
      title: 'Auditoria',
      selectedIndex: 3,
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Wrap(
              spacing: AppSpacing.md,
              runSpacing: AppSpacing.md,
              children: [
                SizedBox(
                  width: 220,
                  child: TextField(
                    controller: _module,
                    decoration: const InputDecoration(labelText: 'Módulo'),
                  ),
                ),
                SizedBox(
                  width: 280,
                  child: TextField(
                    controller: _requestId,
                    decoration: const InputDecoration(labelText: 'Request ID'),
                  ),
                ),
                IconButton(
                  tooltip: 'Filtrar',
                  icon: const Icon(Icons.search),
                  onPressed: () => ref
                      .read(auditControllerProvider.notifier)
                      .reload(
                        module: _module.text.trim(),
                        requestId: _requestId.text.trim(),
                      ),
                ),
              ],
            ),
          ),
          Expanded(
            child: page.when(
              data: (data) => data.items.isEmpty
                  ? const AppEmptyState(
                      title: 'Nenhum evento',
                      message: 'Não há eventos de auditoria para os filtros.',
                    )
                  : LayoutBuilder(
                      builder: (context, constraints) =>
                          constraints.maxWidth >= 900
                          ? _AuditTable(items: data.items)
                          : _AuditCards(items: data.items),
                    ),
              error: (error, stackTrace) =>
                  Center(child: Text(error.toString())),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ),
        ],
      ),
    );
  }
}

class _AuditTable extends StatelessWidget {
  const _AuditTable({required this.items});

  final List<AuditEvent> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Evento')),
          DataColumn(label: Text('Módulo')),
          DataColumn(label: Text('Entidade')),
          DataColumn(label: Text('Request ID')),
          DataColumn(label: Text('Ações')),
        ],
        rows: items
            .map(
              (event) => DataRow(
                cells: [
                  DataCell(Text(event.eventName)),
                  DataCell(Text(event.module)),
                  DataCell(Text(event.entityType ?? '-')),
                  DataCell(Text(event.requestId ?? '-')),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () =>
                          context.go('${AppRoutes.audit}/${event.id}'),
                    ),
                  ),
                ],
              ),
            )
            .toList(),
      ),
    );
  }
}

class _AuditCards extends StatelessWidget {
  const _AuditCards({required this.items});

  final List<AuditEvent> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final event = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.fact_check_outlined),
            title: Text(event.eventName),
            subtitle: Text('${event.module} · ${event.requestId ?? '-'}'),
            trailing: IconButton(
              tooltip: 'Copiar request ID',
              icon: const Icon(Icons.copy),
              onPressed: event.requestId == null
                  ? null
                  : () => Clipboard.setData(
                      ClipboardData(text: event.requestId!),
                    ),
            ),
            onTap: () => context.go('${AppRoutes.audit}/${event.id}'),
          ),
        );
      },
    );
  }
}
