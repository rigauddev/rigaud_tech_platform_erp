import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/inventory.dart';
import '../domain/inventory_input.dart';
import 'inventory_controller.dart';

class InventoryScreen extends ConsumerWidget {
  const InventoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 4,
      child: AppScaffold(
        title: 'Estoque',
        body: Column(
          children: const [
            TabBar(
              tabs: [
                Tab(text: 'Saldos'),
                Tab(text: 'Movimentos'),
                Tab(text: 'Ajuste'),
                Tab(text: 'Reserva'),
              ],
            ),
            Expanded(
              child: TabBarView(
                children: [
                  _BalancesView(),
                  _MovementsView(),
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
                  '${item.movementType} · Físico ${item.physicalQuantityDelta} · Reservado ${item.reservedQuantityDelta}',
                ),
                trailing: Text(item.eventName),
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
          DataColumn(label: Text('Disponível')),
        ],
        rows: items
            .map(
              (item) => DataRow(
                cells: [
                  DataCell(Text(item.productId)),
                  DataCell(Text(item.physicalQuantity)),
                  DataCell(Text(item.reservedQuantity)),
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
              'Físico ${item.physicalQuantity} · Reservado ${item.reservedQuantity}',
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
