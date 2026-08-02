import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/warehouse_zone.dart';
import 'warehouse_zone_controller.dart';

class WarehouseZoneDetailScreen extends ConsumerWidget {
  const WarehouseZoneDetailScreen({required this.zoneId, super.key});

  final String zoneId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final zone = ref.watch(warehouseZoneDetailsProvider(zoneId));
    return AppScaffold(
      title: 'Detalhes da zona',
      body: zone.when(
        data: (item) => _Details(zone: item),
        error: (error, stackTrace) => Center(child: Text(_message(error))),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _Details extends ConsumerWidget {
  const _Details({required this.zone});

  final WarehouseZone zone;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            AppButton(
              label: 'Editar',
              icon: Icons.edit_outlined,
              onPressed: () =>
                  context.go('${AppRoutes.warehouseZones}/${zone.id}/edit'),
            ),
            OutlinedButton.icon(
              icon: Icon(
                zone.isActive
                    ? Icons.pause_circle_outline
                    : Icons.play_circle_outline,
              ),
              label: Text(zone.isActive ? 'Inativar' : 'Ativar'),
              onPressed: () => ref
                  .read(warehouseZonesControllerProvider.notifier)
                  .toggleActive(zone),
            ),
            OutlinedButton.icon(
              icon: const Icon(Icons.swap_vert_outlined),
              label: const Text('Reordenar'),
              onPressed: () => _openReorderDialog(context, ref),
            ),
            OutlinedButton.icon(
              icon: const Icon(Icons.delete_outline),
              label: const Text('Remover'),
              onPressed: () async {
                await ref
                    .read(warehouseZonesControllerProvider.notifier)
                    .deleteZone(zone.id);
                if (context.mounted) {
                  context.go(AppRoutes.warehouseZones);
                }
              },
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  zone.name,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: AppSpacing.sm),
                Text(
                  '${zone.code} · ${zone.type.label} · ${zone.status.label}',
                ),
                const SizedBox(height: AppSpacing.md),
                _row('Ordem', zone.sortOrder.toString()),
                _row('Depósito', zone.warehouseId),
                _row('Descrição', zone.description ?? '-'),
                _row('Cor', zone.color ?? '-'),
                _row('Ícone', zone.icon ?? '-'),
                const Divider(height: AppSpacing.xl),
                _row('Recebimento', zone.isReceiving ? 'Sim' : 'Não'),
                _row('Expedição', zone.isShipping ? 'Sim' : 'Não'),
                _row('Armazenagem', zone.isStorage ? 'Sim' : 'Não'),
                _row('Produção', zone.isProduction ? 'Sim' : 'Não'),
                _row('Quarentena', zone.isQuarantine ? 'Sim' : 'Não'),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 140, child: Text(label)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Future<void> _openReorderDialog(BuildContext context, WidgetRef ref) async {
    final controller = TextEditingController(text: zone.sortOrder.toString());
    final value = await showDialog<int>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Ordenar zona'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(labelText: 'Ordem'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () =>
                Navigator.of(context).pop(int.tryParse(controller.text)),
            child: const Text('Salvar'),
          ),
        ],
      ),
    );
    controller.dispose();
    if (value != null) {
      await ref
          .read(warehouseZonesControllerProvider.notifier)
          .reorder(zone.id, value);
    }
  }
}

String _message(Object error) {
  final text = error.toString();
  if (text.contains('requestId')) {
    return text;
  }
  return 'Não foi possível carregar a zona.';
}
