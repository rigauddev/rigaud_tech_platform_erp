import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../../warehouse_zones/domain/warehouse_zone.dart';
import '../../warehouse_zones/presentation/warehouse_zone_controller.dart';
import '../../warehouses/domain/warehouse.dart';
import '../../warehouses/presentation/warehouse_controller.dart';
import '../domain/warehouse_location.dart';
import 'warehouse_location_controller.dart';

class WarehouseLocationListScreen extends ConsumerStatefulWidget {
  const WarehouseLocationListScreen({super.key});

  @override
  ConsumerState<WarehouseLocationListScreen> createState() =>
      _WarehouseLocationListScreenState();
}

class _WarehouseLocationListScreenState
    extends ConsumerState<WarehouseLocationListScreen> {
  final _search = TextEditingController();
  String? _warehouseId;
  String? _zoneId;

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final locations = ref.watch(warehouseLocationsControllerProvider);
    final warehouses =
        ref.watch(warehousesControllerProvider).value ?? const [];
    final zones = ref.watch(warehouseZonesControllerProvider).value ?? const [];
    return AppScaffold(
      title: 'Localizações',
      actions: [
        IconButton(
          tooltip: 'Nova localização',
          icon: const Icon(Icons.add_location_alt_outlined),
          onPressed: () => context.go(AppRoutes.warehouseLocationCreate),
        ),
      ],
      body: Column(
        children: [
          _Filters(
            search: _search,
            warehouses: warehouses,
            zones: zones,
            warehouseId: _warehouseId,
            zoneId: _zoneId,
            onWarehouseChanged: (value) {
              setState(() {
                _warehouseId = value;
                _zoneId = null;
              });
              _reload();
            },
            onZoneChanged: (value) {
              setState(() => _zoneId = value);
              _reload();
            },
            onSearch: _reload,
          ),
          Expanded(
            child: locations.when(
              data: (items) {
                if (items.isEmpty) {
                  return const AppEmptyState(
                    title: 'Nenhuma localização cadastrada',
                    message:
                        'Crie endereços físicos para organizar estoque por zona.',
                  );
                }
                return LayoutBuilder(
                  builder: (context, constraints) {
                    if (constraints.maxWidth >= 980) {
                      return _WarehouseLocationTable(items: items);
                    }
                    return _WarehouseLocationCards(items: items);
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
        .read(warehouseLocationsControllerProvider.notifier)
        .reload(
          warehouseId: _warehouseId,
          zoneId: _zoneId,
          search: _search.text.trim().isEmpty ? null : _search.text.trim(),
        );
  }
}

class _Filters extends StatelessWidget {
  const _Filters({
    required this.search,
    required this.warehouses,
    required this.zones,
    required this.warehouseId,
    required this.zoneId,
    required this.onWarehouseChanged,
    required this.onZoneChanged,
    required this.onSearch,
  });

  final TextEditingController search;
  final List<Warehouse> warehouses;
  final List<WarehouseZone> zones;
  final String? warehouseId;
  final String? zoneId;
  final ValueChanged<String?> onWarehouseChanged;
  final ValueChanged<String?> onZoneChanged;
  final VoidCallback onSearch;

  @override
  Widget build(BuildContext context) {
    final filteredZones = zones
        .where((zone) => warehouseId == null || zone.warehouseId == warehouseId)
        .toList();
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
            width: 240,
            child: DropdownButtonFormField<String>(
              initialValue: zoneId,
              decoration: const InputDecoration(labelText: 'Zona'),
              items: [
                const DropdownMenuItem(value: null, child: Text('Todas')),
                ...filteredZones.map(
                  (zone) => DropdownMenuItem(
                    value: zone.id,
                    child: Text('${zone.name} · ${zone.code}'),
                  ),
                ),
              ],
              onChanged: onZoneChanged,
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

class _WarehouseLocationTable extends StatelessWidget {
  const _WarehouseLocationTable({required this.items});

  final List<WarehouseLocation> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Ordem')),
          DataColumn(label: Text('Código')),
          DataColumn(label: Text('Nome')),
          DataColumn(label: Text('Endereço')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Ações')),
        ],
        rows: items
            .map(
              (location) => DataRow(
                cells: [
                  DataCell(Text(location.sortOrder.toString())),
                  DataCell(Text(location.code)),
                  DataCell(Text(location.name)),
                  DataCell(Text(_address(location))),
                  DataCell(Text(location.status.label)),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () => context.go(
                        '${AppRoutes.warehouseLocations}/${location.id}',
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

class _WarehouseLocationCards extends StatelessWidget {
  const _WarehouseLocationCards({required this.items});

  final List<WarehouseLocation> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final location = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.location_on_outlined),
            title: Text(location.name),
            subtitle: Text(
              '${location.code} · ${_address(location)} · ${location.status.label}',
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () =>
                context.go('${AppRoutes.warehouseLocations}/${location.id}'),
          ),
        );
      },
    );
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

String _message(Object error) {
  final text = error.toString();
  if (text.contains('requestId')) {
    return text;
  }
  return 'Não foi possível carregar localizações.';
}
