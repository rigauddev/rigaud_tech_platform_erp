import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/warehouse.dart';
import 'warehouse_controller.dart';

class WarehouseDetailScreen extends ConsumerWidget {
  const WarehouseDetailScreen({required this.warehouseId, super.key});

  final String warehouseId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final warehouse = ref.watch(warehouseDetailsProvider(warehouseId));
    return AppScaffold(
      title: 'Depósito',
      actions: [
        IconButton(
          tooltip: 'Editar depósito',
          icon: const Icon(Icons.edit_outlined),
          onPressed: () =>
              context.go('${AppRoutes.warehouses}/$warehouseId/edit'),
        ),
      ],
      body: warehouse.when(
        data: (item) => _WarehouseDetail(item: item),
        error: (error, stackTrace) => Center(child: Text(error.toString())),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _WarehouseDetail extends ConsumerWidget {
  const _WarehouseDetail({required this.item});

  final Warehouse item;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Text(item.name, style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: AppSpacing.sm),
        Text(item.description ?? 'Sem descrição'),
        const SizedBox(height: AppSpacing.lg),
        Wrap(
          spacing: AppSpacing.md,
          runSpacing: AppSpacing.md,
          children: [
            _Info(label: 'Código', value: item.code),
            _Info(label: 'Status', value: item.status.label),
            _Info(label: 'Padrão', value: item.isDefault ? 'Sim' : 'Não'),
            _Info(label: 'Endereço', value: item.address ?? 'Não informado'),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            FilledButton.icon(
              icon: Icon(item.isActive ? Icons.block : Icons.check_circle),
              label: Text(item.isActive ? 'Desativar' : 'Ativar'),
              onPressed: () => ref
                  .read(warehousesControllerProvider.notifier)
                  .toggleActive(item),
            ),
            FilledButton.tonalIcon(
              icon: const Icon(Icons.star_outline),
              label: const Text('Definir padrão'),
              onPressed: item.isDefault
                  ? null
                  : () => ref
                        .read(warehousesControllerProvider.notifier)
                        .setDefault(item.id),
            ),
            OutlinedButton.icon(
              icon: const Icon(Icons.delete_outline),
              label: const Text('Remover'),
              onPressed: () async {
                await ref
                    .read(warehousesControllerProvider.notifier)
                    .deleteWarehouse(item.id);
                if (context.mounted) {
                  context.go(AppRoutes.warehouses);
                }
              },
            ),
          ],
        ),
      ],
    );
  }
}

class _Info extends StatelessWidget {
  const _Info({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 240,
      child: ListTile(
        contentPadding: EdgeInsets.zero,
        title: Text(label),
        subtitle: Text(value),
      ),
    );
  }
}
