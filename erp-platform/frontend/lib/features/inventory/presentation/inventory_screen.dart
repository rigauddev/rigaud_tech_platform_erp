import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../../receiving_documents/domain/receiving_document.dart';
import '../../receiving_documents/presentation/receiving_document_controller.dart';
import '../domain/inventory.dart';
import '../domain/inventory_input.dart';
import 'inventory_controller.dart';

class InventoryScreen extends ConsumerWidget {
  const InventoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 5,
      child: AppScaffold(
        title: 'Estoque',
        body: Column(
          children: const [
            TabBar(
              tabs: [
                Tab(text: 'Saldos'),
                Tab(text: 'Movimentos'),
                Tab(text: 'Put Away'),
                Tab(text: 'Ajuste'),
                Tab(text: 'Reserva'),
              ],
            ),
            Expanded(
              child: TabBarView(
                children: [
                  _BalancesView(),
                  _MovementsView(),
                  _PutAwayView(),
                  _AdjustmentView(),
                  _ReservationView(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _BalancesView extends ConsumerWidget {
  const _BalancesView();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final balances = ref.watch(inventoryBalancesControllerProvider);
    return balances.when(
      data: (items) {
        if (items.isEmpty) {
          return const AppEmptyState(
            title: 'Nenhum saldo encontrado',
            message: 'Registre um ajuste para iniciar o saldo de um produto.',
          );
        }
        return LayoutBuilder(
          builder: (context, constraints) {
            if (constraints.maxWidth >= 900) {
              return _BalanceTable(items: items);
            }
            return _BalanceCards(items: items);
          },
        );
      },
      error: (error, stackTrace) => Center(child: Text(_message(error))),
      loading: () => const Center(child: CircularProgressIndicator()),
    );
  }
}

class _MovementsView extends ConsumerWidget {
  const _MovementsView();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final movements = ref.watch(inventoryMovementsControllerProvider);
    return movements.when(
      data: (items) {
        if (items.isEmpty) {
          return const AppEmptyState(
            title: 'Nenhuma movimentação encontrada',
            message: 'Ajustes e reservas aparecerão neste histórico.',
          );
        }
        return ListView.separated(
          padding: const EdgeInsets.all(AppSpacing.lg),
          itemCount: items.length,
          separatorBuilder: (context, index) =>
              const SizedBox(height: AppSpacing.sm),
          itemBuilder: (context, index) {
            final item = items[index];
            return Card(
              child: ListTile(
                leading: const Icon(Icons.swap_vert_circle_outlined),
                title: Text(item.reason),
                subtitle: Text(
                  '${item.movementType} · Físico ${item.physicalQuantityDelta} · Reservado ${item.reservedQuantityDelta} · Put away ${item.putawayPendingQuantityDelta}',
                ),
                trailing: Text(item.businessProcess),
              ),
            );
          },
        );
      },
      error: (error, stackTrace) => Center(child: Text(_message(error))),
      loading: () => const Center(child: CircularProgressIndicator()),
    );
  }
}

class _PutAwayView extends ConsumerStatefulWidget {
  const _PutAwayView();

  @override
  ConsumerState<_PutAwayView> createState() => _PutAwayViewState();
}

class _PutAwayViewState extends ConsumerState<_PutAwayView> {
  final _documentId = TextEditingController();
  final _productId = TextEditingController();
  final _locationId = TextEditingController();
  final _quantity = TextEditingController();
  final _reason = TextEditingController();

  @override
  void dispose() {
    _documentId.dispose();
    _productId.dispose();
    _locationId.dispose();
    _quantity.dispose();
    _reason.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final wide = constraints.maxWidth >= 960;
        final form = _PutAwayForm(
          documentId: _documentId,
          productId: _productId,
          locationId: _locationId,
          quantity: _quantity,
          reason: _reason,
          onSubmit: _submit,
        );
        final queue = _PutAwayQueue(onSelect: _fillFromQueue);
        final history = const _PutAwayHistory();
        if (wide) {
          return Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(child: form),
                const SizedBox(width: AppSpacing.lg),
                Expanded(
                  child: Column(
                    children: [
                      queue,
                      const SizedBox(height: AppSpacing.lg),
                      history,
                    ],
                  ),
                ),
              ],
            ),
          );
        }
        return ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            queue,
            const SizedBox(height: AppSpacing.lg),
            form,
            const SizedBox(height: AppSpacing.lg),
            history,
          ],
        );
      },
    );
  }

  void _fillFromQueue(ReceivingDocument document) {
    final item = document.items.firstOrNull;
    _documentId.text = document.id;
    _productId.text = item?.productId ?? '';
    _quantity.text = item?.receivedQuantity.toStringAsFixed(3) ?? '';
  }

  Future<void> _submit() async {
    final result = await ref
        .read(inventoryBalancesControllerProvider.notifier)
        .confirmPutAway(
          PutAwayInput(
            documentId: _documentId.text.trim(),
            productId: _productId.text.trim(),
            locationId: _locationId.text.trim(),
            quantity: _quantity.text.trim(),
            reason: _reason.text.trim(),
          ),
        );
    if (result != null && mounted) {
      _showSuccess(context, 'Put Away confirmado.');
    }
  }
}

class _PutAwayQueue extends ConsumerWidget {
  const _PutAwayQueue({required this.onSelect});

  final ValueChanged<ReceivingDocument> onSelect;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final documents = ref.watch(receivingDocumentsControllerProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Documentos pendentes',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: AppSpacing.lg),
            documents.when(
              data: (items) {
                final pending = items
                    .where(
                      (item) =>
                          item.status == ReceivingDocumentStatus.putawayPending,
                    )
                    .toList();
                if (pending.isEmpty) {
                  return const AppEmptyState(
                    title: 'Fila vazia',
                    message:
                        'Documentos recebidos e pendentes de armazenagem aparecerão aqui.',
                  );
                }
                return Column(
                  children: [
                    for (final item in pending)
                      ListTile(
                        leading: const Icon(Icons.inventory_2_outlined),
                        title: Text(item.documentNumber),
                        subtitle: Text(
                          'Warehouse ${item.warehouseId} · Itens ${item.items.length}',
                        ),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => onSelect(item),
                      ),
                  ],
                );
              },
              error: (error, stackTrace) => Text(_message(error)),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ],
        ),
      ),
    );
  }
}

class _PutAwayForm extends StatelessWidget {
  const _PutAwayForm({
    required this.documentId,
    required this.productId,
    required this.locationId,
    required this.quantity,
    required this.reason,
    required this.onSubmit,
  });

  final TextEditingController documentId;
  final TextEditingController productId;
  final TextEditingController locationId;
  final TextEditingController quantity;
  final TextEditingController reason;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Fila de Put Away',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Confirme a armazenagem física de itens recebidos em uma localização ativa.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: AppSpacing.lg),
            TextField(
              controller: documentId,
              decoration: const InputDecoration(
                labelText: 'Documento de recebimento ID',
              ),
            ),
            const SizedBox(height: AppSpacing.md),
            TextField(
              controller: productId,
              decoration: const InputDecoration(labelText: 'Produto ID'),
            ),
            const SizedBox(height: AppSpacing.md),
            TextField(
              controller: locationId,
              decoration: const InputDecoration(labelText: 'Localização ID'),
            ),
            const SizedBox(height: AppSpacing.md),
            TextField(
              controller: quantity,
              decoration: const InputDecoration(labelText: 'Quantidade'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: AppSpacing.md),
            TextField(
              controller: reason,
              decoration: const InputDecoration(labelText: 'Observação'),
            ),
            const SizedBox(height: AppSpacing.lg),
            FilledButton.icon(
              onPressed: onSubmit,
              icon: const Icon(Icons.move_down_outlined),
              label: const Text('Confirmar Put Away'),
            ),
          ],
        ),
      ),
    );
  }
}

class _PutAwayHistory extends ConsumerWidget {
  const _PutAwayHistory();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final movements = ref.watch(inventoryMovementsControllerProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Histórico de armazenagens',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: AppSpacing.lg),
            movements.when(
              data: (items) {
                final putaways = items
                    .where((item) => item.businessProcess == 'PUTAWAY')
                    .toList();
                if (putaways.isEmpty) {
                  return const AppEmptyState(
                    title: 'Nenhum Put Away confirmado',
                    message: 'As armazenagens confirmadas aparecerão aqui.',
                  );
                }
                return Column(
                  children: [
                    for (final item in putaways)
                      ListTile(
                        leading: const Icon(Icons.shelves),
                        title: Text(item.reason),
                        subtitle: Text(
                          'Produto ${item.productId} · Quantidade ${item.putawayPendingQuantityDelta}',
                        ),
                        trailing: Text(item.originModule),
                      ),
                  ],
                );
              },
              error: (error, stackTrace) => Text(_message(error)),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ],
        ),
      ),
    );
  }
}

class _AdjustmentView extends ConsumerStatefulWidget {
  const _AdjustmentView();

  @override
  ConsumerState<_AdjustmentView> createState() => _AdjustmentViewState();
}

class _AdjustmentViewState extends ConsumerState<_AdjustmentView> {
  final _productId = TextEditingController();
  final _quantity = TextEditingController();
  final _reason = TextEditingController();
  InventoryAdjustmentType _type = InventoryAdjustmentType.increase;

  @override
  void dispose() {
    _productId.dispose();
    _quantity.dispose();
    _reason.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _OperationForm(
      title: 'Ajuste de estoque',
      actionLabel: 'Registrar ajuste',
      productId: _productId,
      quantity: _quantity,
      reason: _reason,
      leading: DropdownButtonFormField<InventoryAdjustmentType>(
        initialValue: _type,
        decoration: const InputDecoration(labelText: 'Tipo'),
        items: InventoryAdjustmentType.values
            .map(
              (type) => DropdownMenuItem(value: type, child: Text(type.label)),
            )
            .toList(),
        onChanged: (value) => setState(() => _type = value ?? _type),
      ),
      onSubmit: () async {
        final result = await ref
            .read(inventoryBalancesControllerProvider.notifier)
            .createAdjustment(
              InventoryAdjustmentInput(
                productId: _productId.text.trim(),
                adjustmentType: _type,
                quantity: _quantity.text.trim(),
                reason: _reason.text.trim(),
              ),
            );
        if (result != null && context.mounted) {
          _showSuccess(context, 'Ajuste registrado.');
        }
      },
    );
  }
}

class _ReservationView extends ConsumerStatefulWidget {
  const _ReservationView();

  @override
  ConsumerState<_ReservationView> createState() => _ReservationViewState();
}

class _ReservationViewState extends ConsumerState<_ReservationView> {
  final _productId = TextEditingController();
  final _quantity = TextEditingController();
  final _reason = TextEditingController();

  @override
  void dispose() {
    _productId.dispose();
    _quantity.dispose();
    _reason.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _OperationForm(
      title: 'Reserva de estoque',
      actionLabel: 'Registrar reserva',
      productId: _productId,
      quantity: _quantity,
      reason: _reason,
      onSubmit: () async {
        final result = await ref
            .read(inventoryBalancesControllerProvider.notifier)
            .createReservation(
              InventoryReservationInput(
                productId: _productId.text.trim(),
                quantity: _quantity.text.trim(),
                reason: _reason.text.trim(),
                sourceModule: 'manual',
              ),
            );
        if (result != null && context.mounted) {
          _showSuccess(context, 'Reserva registrada.');
        }
      },
    );
  }
}

class _OperationForm extends StatelessWidget {
  const _OperationForm({
    required this.title,
    required this.actionLabel,
    required this.productId,
    required this.quantity,
    required this.reason,
    required this.onSubmit,
    this.leading,
  });

  final String title;
  final String actionLabel;
  final TextEditingController productId;
  final TextEditingController quantity;
  final TextEditingController reason;
  final VoidCallback onSubmit;
  final Widget? leading;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(title, style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: AppSpacing.lg),
              if (leading != null) ...[
                leading!,
                const SizedBox(height: AppSpacing.md),
              ],
              TextField(
                controller: productId,
                decoration: const InputDecoration(labelText: 'Produto ID'),
              ),
              const SizedBox(height: AppSpacing.md),
              TextField(
                controller: quantity,
                decoration: const InputDecoration(labelText: 'Quantidade'),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: AppSpacing.md),
              TextField(
                controller: reason,
                decoration: const InputDecoration(labelText: 'Motivo'),
              ),
              const SizedBox(height: AppSpacing.lg),
              FilledButton.icon(
                onPressed: onSubmit,
                icon: const Icon(Icons.save_outlined),
                label: Text(actionLabel),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _BalanceTable extends StatelessWidget {
  const _BalanceTable({required this.items});

  final List<InventoryBalance> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Produto')),
          DataColumn(label: Text('Físico')),
          DataColumn(label: Text('Reservado')),
          DataColumn(label: Text('Put away')),
          DataColumn(label: Text('Disponível')),
        ],
        rows: items
            .map(
              (item) => DataRow(
                cells: [
                  DataCell(Text(item.productId)),
                  DataCell(Text(item.physicalQuantity)),
                  DataCell(Text(item.reservedQuantity)),
                  DataCell(Text(item.putawayPendingQuantity)),
                  DataCell(Text(item.availableQuantity)),
                ],
              ),
            )
            .toList(),
      ),
    );
  }
}

class _BalanceCards extends StatelessWidget {
  const _BalanceCards({required this.items});

  final List<InventoryBalance> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final item = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.inventory_outlined),
            title: Text(item.productId),
            subtitle: Text(
              'Físico ${item.physicalQuantity} · Reservado ${item.reservedQuantity} · Put away ${item.putawayPendingQuantity}',
            ),
            trailing: Text(item.availableQuantity),
          ),
        );
      },
    );
  }
}

void _showSuccess(BuildContext context, String message) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
}

String _message(Object error) {
  final text = error.toString();
  if (text.contains('requestId')) {
    return text;
  }
  return 'Não foi possível carregar estoque.';
}
