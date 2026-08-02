import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/warehouse_zone.dart';
import 'warehouse_zone_controller.dart';

class WarehouseZoneListScreen extends ConsumerWidget {
  const WarehouseZoneListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final zones = ref.watch(warehouseZonesControllerProvider);
    return AppScaffold(
      title: 'Zonas',
      actions: [
        IconButton(
          tooltip: 'Nova zona',
          icon: const Icon(Icons.add_location_alt_outlined),
          onPressed: () => context.go(AppRoutes.warehouseZoneCreate),
        ),
      ],
      body: zones.when(
        data: (items) {
          if (items.isEmpty) {
            return const AppEmptyState(
              title: 'Nenhuma zona cadastrada',
              message:
                  'Crie zonas para organizar recebimento, estoque e expedição.',
            );
          }
          return LayoutBuilder(
            builder: (context, constraints) {
              if (constraints.maxWidth >= 920) {
                return _WarehouseZoneTable(items: items);
              }
              return _WarehouseZoneCards(items: items);
            },
          );
        },
        error: (error, stackTrace) => Center(child: Text(_message(error))),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _WarehouseZoneTable extends StatelessWidget {
  const _WarehouseZoneTable({required this.items});

  final List<WarehouseZone> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Ordem')),
          DataColumn(label: Text('Nome')),
          DataColumn(label: Text('Código')),
          DataColumn(label: Text('Tipo')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Ações')),
        ],
        rows: items
            .map(
              (zone) => DataRow(
                cells: [
                  DataCell(Text(zone.sortOrder.toString())),
                  DataCell(Text(zone.name)),
                  DataCell(Text(zone.code)),
                  DataCell(Text(zone.type.label)),
                  DataCell(Text(zone.status.label)),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () =>
                          context.go('${AppRoutes.warehouseZones}/${zone.id}'),
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

class _WarehouseZoneCards extends StatelessWidget {
  const _WarehouseZoneCards({required this.items});

  final List<WarehouseZone> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final zone = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.location_searching_outlined),
            title: Text(zone.name),
            subtitle: Text(
              '${zone.code} · ${zone.type.label} · ${zone.status.label}',
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go('${AppRoutes.warehouseZones}/${zone.id}'),
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
  return 'Não foi possível carregar zonas.';
}
