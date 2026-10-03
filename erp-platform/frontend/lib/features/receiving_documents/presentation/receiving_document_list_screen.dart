import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../../warehouses/domain/warehouse.dart';
import '../../warehouses/presentation/warehouse_controller.dart';
import '../domain/receiving_document.dart';
import 'receiving_document_controller.dart';

class ReceivingDocumentListScreen extends ConsumerStatefulWidget {
  const ReceivingDocumentListScreen({super.key});

  @override
  ConsumerState<ReceivingDocumentListScreen> createState() =>
      _ReceivingDocumentListScreenState();
}

class _ReceivingDocumentListScreenState
    extends ConsumerState<ReceivingDocumentListScreen> {
  final _search = TextEditingController();
  String? _warehouseId;
  ReceivingDocumentStatus? _status;

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final documents = ref.watch(receivingDocumentsControllerProvider);
    final warehouses =
        ref.watch(warehousesControllerProvider).value ?? const [];
    return AppScaffold(
      title: 'Recebimentos',
      actions: [
        IconButton(
          tooltip: 'Novo recebimento',
          icon: const Icon(Icons.add_box_outlined),
          onPressed: () => context.go(AppRoutes.receivingDocumentCreate),
        ),
      ],
      body: Column(
        children: [
          _Filters(
            search: _search,
            warehouses: warehouses,
            warehouseId: _warehouseId,
            status: _status,
            onWarehouseChanged: (value) {
              setState(() => _warehouseId = value);
              _reload();
            },
            onStatusChanged: (value) {
              setState(() => _status = value);
              _reload();
            },
            onSearch: _reload,
          ),
          Expanded(
            child: documents.when(
              data: (items) {
                if (items.isEmpty) {
                  return const AppEmptyState(
                    title: 'Nenhum recebimento cadastrado',
                    message:
                        'Registre documentos de entrada antes da movimentacao fisica.',
                  );
                }
                return LayoutBuilder(
                  builder: (context, constraints) {
                    if (constraints.maxWidth >= 920) {
                      return _ReceivingDocumentTable(items: items);
                    }
                    return _ReceivingDocumentCards(items: items);
                  },
                );
              },
              error: (error, stackTrace) =>
                  Center(child: Text(_message(error))),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ),
        ],
      ),
    );
  }

  void _reload() {
    ref
        .read(receivingDocumentsControllerProvider.notifier)
        .reload(
          warehouseId: _warehouseId,
          status: _status,
          search: _search.text.trim().isEmpty ? null : _search.text.trim(),
        );
  }
}

class _Filters extends StatelessWidget {
  const _Filters({
    required this.search,
    required this.warehouses,
    required this.warehouseId,
    required this.status,
    required this.onWarehouseChanged,
    required this.onStatusChanged,
    required this.onSearch,
  });

  final TextEditingController search;
  final List<Warehouse> warehouses;
  final String? warehouseId;
  final ReceivingDocumentStatus? status;
  final ValueChanged<String?> onWarehouseChanged;
  final ValueChanged<ReceivingDocumentStatus?> onStatusChanged;
  final VoidCallback onSearch;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Wrap(
        spacing: AppSpacing.md,
        runSpacing: AppSpacing.md,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          SizedBox(
            width: 260,
            child: TextField(
              controller: search,
              decoration: const InputDecoration(
                labelText: 'Pesquisar',
                prefixIcon: Icon(Icons.search),
              ),
              onSubmitted: (_) => onSearch(),
            ),
          ),
          SizedBox(
            width: 260,
            child: DropdownButtonFormField<String>(
              initialValue: warehouseId,
              decoration: const InputDecoration(labelText: 'Depósito'),
              items: [
                const DropdownMenuItem(value: null, child: Text('Todos')),
                ...warehouses.map(
                  (warehouse) => DropdownMenuItem(
                    value: warehouse.id,
                    child: Text('${warehouse.name} · ${warehouse.code}'),
                  ),
                ),
              ],
              onChanged: onWarehouseChanged,
            ),
          ),
          SizedBox(
            width: 220,
            child: DropdownButtonFormField<ReceivingDocumentStatus>(
              initialValue: status,
              decoration: const InputDecoration(labelText: 'Status'),
              items: [
                const DropdownMenuItem(value: null, child: Text('Todos')),
                ...ReceivingDocumentStatus.values.map(
                  (value) =>
                      DropdownMenuItem(value: value, child: Text(value.label)),
                ),
              ],
              onChanged: onStatusChanged,
            ),
          ),
          IconButton(
            tooltip: 'Aplicar filtros',
            icon: const Icon(Icons.tune_outlined),
            onPressed: onSearch,
          ),
        ],
      ),
    );
  }
}

class _ReceivingDocumentTable extends StatelessWidget {
  const _ReceivingDocumentTable({required this.items});

  final List<ReceivingDocument> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Documento')),
          DataColumn(label: Text('Tipo')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Itens')),
          DataColumn(label: Text('Pendente')),
          DataColumn(label: Text('Ações')),
        ],
        rows: items
            .map(
              (document) => DataRow(
                cells: [
                  DataCell(Text(document.documentNumber)),
                  DataCell(Text(document.documentType)),
                  DataCell(Text(document.status.label)),
                  DataCell(Text(document.items.length.toString())),
                  DataCell(Text(document.pendingTotal.toStringAsFixed(3))),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () => context.go(
                        '${AppRoutes.receivingDocuments}/${document.id}',
                      ),
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

class _ReceivingDocumentCards extends StatelessWidget {
  const _ReceivingDocumentCards({required this.items});

  final List<ReceivingDocument> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final document = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.inventory_outlined),
            title: Text(document.documentNumber),
            subtitle: Text(
              '${document.documentType} · ${document.status.label} · ${document.items.length} itens',
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () =>
                context.go('${AppRoutes.receivingDocuments}/${document.id}'),
          ),
        );
      },
    );
  }
}

String _message(Object error) {
  final text = error.toString();
  if (text.contains('requestId')) {
    return text;
  }
  return 'Não foi possível carregar recebimentos.';
}
