import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/warehouse.dart';
import 'warehouse_controller.dart';

class WarehouseListScreen extends ConsumerWidget {
  const WarehouseListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final warehouses = ref.watch(warehousesControllerProvider);
    return AppScaffold(
      title: 'Depósitos',
      actions: [
        IconButton(
          tooltip: 'Novo depósito',
          icon: const Icon(Icons.add_business_outlined),
          onPressed: () => context.go(AppRoutes.warehouseCreate),
        ),
      ],
      body: warehouses.when(
        data: (items) {
          if (items.isEmpty) {
            return const AppEmptyState(
              title: 'Nenhum depósito cadastrado',
              message: 'Crie depósitos para organizar o saldo por filial.',
            );
          }
          return LayoutBuilder(
            builder: (context, constraints) {
              if (constraints.maxWidth >= 900) {
                return _WarehouseTable(items: items);
              }
              return _WarehouseCards(items: items);
            },
          );
        },
        error: (error, stackTrace) => Center(child: Text(_message(error))),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _WarehouseTable extends StatelessWidget {
  const _WarehouseTable({required this.items});

  final List<Warehouse> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Nome')),
          DataColumn(label: Text('Código')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Padrão')),
          DataColumn(label: Text('Ações')),
        ],
        rows: items
            .map(
              (warehouse) => DataRow(
                cells: [
                  DataCell(Text(warehouse.name)),
                  DataCell(Text(warehouse.code)),
                  DataCell(Text(warehouse.status.label)),
                  DataCell(Text(warehouse.isDefault ? 'Sim' : 'Não')),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () =>
                          context.go('${AppRoutes.warehouses}/${warehouse.id}'),
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

class _WarehouseCards extends StatelessWidget {
  const _WarehouseCards({required this.items});

  final List<Warehouse> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final warehouse = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.warehouse_outlined),
            title: Text(warehouse.name),
            subtitle: Text(
              '${warehouse.code} · ${warehouse.status.label}${warehouse.isDefault ? ' · Padrão' : ''}',
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go('${AppRoutes.warehouses}/${warehouse.id}'),
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
  return 'Não foi possível carregar depósitos.';
}
