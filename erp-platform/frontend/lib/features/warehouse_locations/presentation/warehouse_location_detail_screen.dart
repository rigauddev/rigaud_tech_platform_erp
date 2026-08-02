import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/warehouse_location.dart';
import 'warehouse_location_controller.dart';

class WarehouseLocationDetailScreen extends ConsumerWidget {
  const WarehouseLocationDetailScreen({required this.locationId, super.key});

  final String locationId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location = ref.watch(warehouseLocationDetailsProvider(locationId));
    return AppScaffold(
      title: 'Detalhes da localização',
      body: location.when(
        data: (item) => _Details(location: item),
        error: (error, stackTrace) => Center(child: Text(_message(error))),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _Details extends ConsumerWidget {
  const _Details({required this.location});

  final WarehouseLocation location;

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
              onPressed: () => context.go(
                '${AppRoutes.warehouseLocations}/${location.id}/edit',
              ),
            ),
            OutlinedButton.icon(
              icon: Icon(
                location.isActive
                    ? Icons.pause_circle_outline
                    : Icons.play_circle_outline,
              ),
              label: Text(location.isActive ? 'Inativar' : 'Ativar'),
              onPressed: () => location.isActive
                  ? ref
                        .read(warehouseLocationsControllerProvider.notifier)
                        .deactivate(location.id)
                  : ref
                        .read(warehouseLocationsControllerProvider.notifier)
                        .activate(location.id),
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
                    .read(warehouseLocationsControllerProvider.notifier)
                    .deleteLocation(location.id);
                if (context.mounted) {
                  context.go(AppRoutes.warehouseLocations);
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
                  location.name,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: AppSpacing.sm),
                Text('${location.code} · ${location.status.label}'),
                const SizedBox(height: AppSpacing.md),
                _row('Apelido', location.alias ?? '-'),
                _row('Endereço', _address(location)),
                _row('Depósito', location.warehouseId),
                _row('Zona', location.zoneId),
                _row('Código de barras', location.barcode ?? '-'),
                _row('QR Code', location.qrCode ?? '-'),
                _row('Capacidade', _capacity(location)),
                _row('Ordem', location.sortOrder.toString()),
                const Divider(height: AppSpacing.xl),
                _row('Saldo negativo', location.allowNegative ? 'Sim' : 'Não'),
                _row('Itens mistos', location.allowMixedItems ? 'Sim' : 'Não'),
                _row('Vencidos', location.allowExpired ? 'Sim' : 'Não'),
                _row('Picking', location.isPickLocation ? 'Sim' : 'Não'),
                _row('Recebimento', location.isReceiveLocation ? 'Sim' : 'Não'),
                _row('Expedição', location.isShippingLocation ? 'Sim' : 'Não'),
                _row('Padrão', location.isDefault ? 'Sim' : 'Não'),
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
          SizedBox(width: 150, child: Text(label)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Future<void> _openReorderDialog(BuildContext context, WidgetRef ref) async {
    final controller = TextEditingController(
      text: location.sortOrder.toString(),
    );
    final value = await showDialog<int>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Ordenar localização'),
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
          .read(warehouseLocationsControllerProvider.notifier)
          .reorder(location.id, value);
    }
  }
}

String _address(WarehouseLocation location) {
  final parts = [
    location.aisle,
    location.rack,
    location.shelf,
    location.level,
    location.position,
  ].whereType<String>().where((item) => item.isNotEmpty).toList();
  return parts.isEmpty ? '-' : parts.join('-');
}

String _capacity(WarehouseLocation location) {
  if (location.capacity == null) {
    return '-';
  }
  final unit = location.capacityUnit ?? '';
  return '${location.capacity} $unit'.trim();
}

String _message(Object error) {
  final text = error.toString();
  if (text.contains('requestId')) {
    return text;
  }
  return 'Não foi possível carregar a localização.';
}
