import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/restaurant_table.dart';
import 'restaurant_tables_controller.dart';

class RestaurantTablesScreen extends ConsumerStatefulWidget {
  const RestaurantTablesScreen({super.key});
  @override
  ConsumerState<RestaurantTablesScreen> createState() =>
      _RestaurantTablesScreenState();
}

class _RestaurantTablesScreenState
    extends ConsumerState<RestaurantTablesScreen> {
  String? _floorId;
  RestaurantTable? _selected;

  @override
  Widget build(BuildContext context) {
    final floors = ref.watch(restaurantFloorsProvider);
    return AppScaffold(
      title: 'Mesas e mapa do salão',
      body: floors.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) =>
            Center(child: Text('Não foi possível carregar os salões.')),
        data: (items) {
          if (items.isEmpty) {
            return const AppEmptyState(
              title: 'Nenhum salão cadastrado',
              message: 'Cadastre um salão para organizar mesas e atendimento.',
            );
          }
          final current = items.any((item) => item.id == _floorId)
              ? _floorId!
              : items.first.id;
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  AppSpacing.lg,
                  AppSpacing.lg,
                  AppSpacing.lg,
                  0,
                ),
                child: DropdownButtonFormField<String>(
                  initialValue: current,
                  decoration: const InputDecoration(labelText: 'Salão'),
                  items: items
                      .where((item) => item.isActive)
                      .map(
                        (item) => DropdownMenuItem(
                          value: item.id,
                          child: Text(item.name),
                        ),
                      )
                      .toList(),
                  onChanged: (value) => setState(() {
                    _floorId = value;
                    _selected = null;
                  }),
                ),
              ),
              Expanded(
                child: _TablesBody(
                  floorId: current,
                  selected: _selected,
                  onSelected: (table) => setState(() => _selected = table),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _TablesBody extends ConsumerWidget {
  const _TablesBody({
    required this.floorId,
    required this.selected,
    required this.onSelected,
  });
  final String floorId;
  final RestaurantTable? selected;
  final ValueChanged<RestaurantTable> onSelected;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tables = ref.watch(restaurantTablesProvider(floorId));
    return tables.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) =>
          Center(child: Text('Não foi possível carregar as mesas.')),
      data: (items) {
        if (items.isEmpty) {
          return const AppEmptyState(
            title: 'Nenhuma mesa cadastrada',
            message: 'As mesas deste salão aparecerão no mapa operacional.',
          );
        }
        return LayoutBuilder(
          builder: (context, constraints) {
            if (constraints.maxWidth < 900) {
              return _TableList(
                items: items,
                selected: selected,
                onSelected: onSelected,
              );
            }
            return Padding(
              padding: const EdgeInsets.all(AppSpacing.lg),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(
                    child: _FloorMap(
                      items: items,
                      selected: selected,
                      onSelected: onSelected,
                    ),
                  ),
                  const SizedBox(width: AppSpacing.lg),
                  SizedBox(width: 280, child: _TableDetails(table: selected)),
                ],
              ),
            );
          },
        );
      },
    );
  }
}

class _FloorMap extends StatelessWidget {
  const _FloorMap({
    required this.items,
    required this.selected,
    required this.onSelected,
  });
  final List<RestaurantTable> items;
  final RestaurantTable? selected;
  final ValueChanged<RestaurantTable> onSelected;
  @override
  Widget build(BuildContext context) => DecoratedBox(
    decoration: BoxDecoration(
      color: Theme.of(context).colorScheme.surfaceContainerLowest,
      border: Border.all(color: Theme.of(context).dividerColor),
      borderRadius: BorderRadius.circular(8),
    ),
    child: LayoutBuilder(
      builder: (context, constraints) => Stack(
        children: [
          const Positioned(
            left: 20,
            top: 16,
            child: Text(
              'Mapa operacional',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
          ...items.map(
            (item) => Positioned(
              left: (item.positionX / 1000 * (constraints.maxWidth - 120))
                  .clamp(0, constraints.maxWidth - 100),
              top: (item.positionY / 700 * (constraints.maxHeight - 100)).clamp(
                56,
                constraints.maxHeight - 84,
              ),
              child: _TableTile(
                table: item,
                selected: selected?.id == item.id,
                onTap: () => onSelected(item),
              ),
            ),
          ),
        ],
      ),
    ),
  );
}

class _TableList extends StatelessWidget {
  const _TableList({
    required this.items,
    required this.selected,
    required this.onSelected,
  });
  final List<RestaurantTable> items;
  final RestaurantTable? selected;
  final ValueChanged<RestaurantTable> onSelected;
  @override
  Widget build(BuildContext context) => ListView.separated(
    padding: const EdgeInsets.all(AppSpacing.lg),
    itemCount: items.length,
    separatorBuilder: (context, index) => const SizedBox(height: AppSpacing.sm),
    itemBuilder: (context, index) {
      final table = items[index];
      return Card(
        child: ListTile(
          selected: selected?.id == table.id,
          leading: _StatusDot(status: table.status),
          title: Text('Mesa ${table.number}'),
          subtitle: Text('${table.capacity} lugares · ${table.status.label}'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => onSelected(table),
        ),
      );
    },
  );
}

class _TableTile extends StatelessWidget {
  const _TableTile({
    required this.table,
    required this.selected,
    required this.onTap,
  });
  final RestaurantTable table;
  final bool selected;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Tooltip(
    message: 'Mesa ${table.number}: ${table.status.label}',
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(
        table.shape == RestaurantTableShape.round ? 100 : 8,
      ),
      child: Container(
        width: table.width.clamp(64, 150),
        height: table.height.clamp(54, 120),
        decoration: BoxDecoration(
          color: _color(context, table.status),
          borderRadius: BorderRadius.circular(
            table.shape == RestaurantTableShape.round ? 100 : 8,
          ),
          border: selected
              ? Border.all(
                  color: Theme.of(context).colorScheme.primary,
                  width: 3,
                )
              : null,
        ),
        alignment: Alignment.center,
        child: Text(
          'Mesa\n${table.number}',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Theme.of(context).colorScheme.onPrimaryContainer,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    ),
  );
}

class _TableDetails extends StatelessWidget {
  const _TableDetails({required this.table});
  final RestaurantTable? table;
  @override
  Widget build(BuildContext context) {
    if (table == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(AppSpacing.lg),
          child: Text('Selecione uma mesa no mapa para consultar seu status.'),
        ),
      );
    }
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Mesa ${table!.number}',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: AppSpacing.md),
            Text(table!.status.label),
            const SizedBox(height: AppSpacing.sm),
            Text('${table!.capacity} lugares'),
            if (table!.qrCode != null) ...[
              const SizedBox(height: AppSpacing.sm),
              const Text('QR reservado para ativação futura'),
            ],
          ],
        ),
      ),
    );
  }
}

class _StatusDot extends StatelessWidget {
  const _StatusDot({required this.status});
  final RestaurantTableStatus status;
  @override
  Widget build(BuildContext context) =>
      CircleAvatar(radius: 10, backgroundColor: _color(context, status));
}

Color _color(BuildContext context, RestaurantTableStatus status) =>
    switch (status) {
      RestaurantTableStatus.available => Colors.green.shade200,
      RestaurantTableStatus.occupied => Colors.orange.shade200,
      RestaurantTableStatus.reserved => Colors.blue.shade200,
      RestaurantTableStatus.orderPending ||
      RestaurantTableStatus.kitchen => Colors.amber.shade200,
      RestaurantTableStatus.waitingPayment => Colors.purple.shade100,
      RestaurantTableStatus.cleaning => Colors.grey.shade300,
      RestaurantTableStatus.blocked => Colors.red.shade200,
    };
