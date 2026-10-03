import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../app/router/app_routes.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../data/restaurant_sector_remote_data_source.dart';

class RestaurantSectorsScreen extends ConsumerWidget {
  const RestaurantSectorsScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sectors = ref.watch(restaurantSectorsProvider);
    return AppScaffold(
      title: 'Setores e ambientes',
      actions: [
        IconButton(
          tooltip: 'Novo setor',
          onPressed: () => context.go(AppRoutes.restaurantSectorCreate),
          icon: const Icon(Icons.add_business_outlined),
        ),
      ],
      body: sectors.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) =>
            Center(child: Text('Não foi possível carregar os setores.')),
        data: (items) {
          if (items.isEmpty) {
            return const AppEmptyState(
              title: 'Nenhum setor cadastrado',
              message:
                  'Cadastre setores para organizar o atendimento da filial.',
            );
          }
          final active = items.where((item) => item.isActive).length;
          return ListView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            children: [
              Text(
                'Setores e ambientes',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                'Organize os ambientes do restaurante e sua capacidade de atendimento.',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: AppSpacing.lg),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  _Metric(
                    label: 'Setores',
                    value: '${items.length}',
                    icon: Icons.grid_view_outlined,
                  ),
                  _Metric(
                    label: 'Setores ativos',
                    value: '$active',
                    icon: Icons.verified_outlined,
                    isSuccess: true,
                  ),
                  _Metric(
                    label: 'Capacidade',
                    value: 'Em configuração',
                    icon: Icons.people_outline,
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              LayoutBuilder(
                builder: (context, constraints) {
                  if (constraints.maxWidth >= 900) {
                    return _DesktopSectors(items: items);
                  }
                  return _MobileSectors(items: items);
                },
              ),
            ],
          );
        },
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({
    required this.label,
    required this.value,
    required this.icon,
    this.isSuccess = false,
  });
  final String label, value;
  final IconData icon;
  final bool isSuccess;
  @override
  Widget build(BuildContext context) => SizedBox(
    width: 240,
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.md),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: (isSuccess ? AppColors.success : AppColors.brand)
                  .withValues(alpha: .12),
              child: Icon(
                icon,
                color: isSuccess ? AppColors.success : AppColors.brand,
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(value, style: Theme.of(context).textTheme.titleLarge),
                Text(label),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}

class _DesktopSectors extends StatelessWidget {
  const _DesktopSectors({required this.items});
  final List<RestaurantSector> items;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        'Ambientes da filial',
        style: Theme.of(context).textTheme.titleLarge,
      ),
      const SizedBox(height: AppSpacing.md),
      Wrap(
        spacing: AppSpacing.md,
        runSpacing: AppSpacing.md,
        children: items
            .map((item) => SizedBox(width: 260, child: _SectorCard(item: item)))
            .toList(),
      ),
      const SizedBox(height: AppSpacing.xl),
      Text(
        'Organização operacional',
        style: Theme.of(context).textTheme.titleLarge,
      ),
      const SizedBox(height: AppSpacing.md),
      Card(
        child: DataTable(
          columns: const [
            DataColumn(label: Text('Setor')),
            DataColumn(label: Text('Tipo')),
            DataColumn(label: Text('Status')),
            DataColumn(label: Text('Ações')),
          ],
          rows: items
              .map(
                (item) => DataRow(
                  cells: [
                    DataCell(Text(item.name)),
                    DataCell(Text(_typeLabel(item.type))),
                    DataCell(_Status(active: item.isActive)),
                    DataCell(
                      IconButton(
                        tooltip: 'Editar setor',
                        onPressed: () => context.go(
                          AppRoutes.restaurantSectorEdit(item.id),
                          extra: item,
                        ),
                        icon: const Icon(Icons.more_vert),
                      ),
                    ),
                  ],
                ),
              )
              .toList(),
        ),
      ),
    ],
  );
}

class _MobileSectors extends StatelessWidget {
  const _MobileSectors({required this.items});
  final List<RestaurantSector> items;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        'Ambientes da filial',
        style: Theme.of(context).textTheme.titleLarge,
      ),
      const SizedBox(height: AppSpacing.md),
      ...items.map(
        (item) => Padding(
          padding: const EdgeInsets.only(bottom: AppSpacing.sm),
          child: _SectorCard(item: item),
        ),
      ),
    ],
  );
}

class _SectorCard extends StatelessWidget {
  const _SectorCard({required this.item});
  final RestaurantSector item;
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                backgroundColor: AppColors.brand.withValues(alpha: .1),
                child: Icon(_icon(item.type), color: AppColors.brand),
              ),
              const Spacer(),
              IconButton(
                tooltip: 'Editar setor',
                onPressed: () => context.go(
                  AppRoutes.restaurantSectorEdit(item.id),
                  extra: item,
                ),
                icon: const Icon(Icons.more_vert),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(item.name, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: AppSpacing.xs),
          Text(_typeLabel(item.type)),
          const SizedBox(height: AppSpacing.md),
          _Status(active: item.isActive),
        ],
      ),
    ),
  );
}

class _Status extends StatelessWidget {
  const _Status({required this.active});
  final bool active;
  @override
  Widget build(BuildContext context) => Chip(
    avatar: Icon(
      Icons.circle,
      size: 10,
      color: active ? AppColors.success : AppColors.warning,
    ),
    label: Text(active ? 'Ativo' : 'Inativo'),
  );
}

IconData _icon(RestaurantSectorType type) => switch (type) {
  RestaurantSectorType.diningRoom => Icons.table_restaurant_outlined,
  RestaurantSectorType.outdoor => Icons.deck_outlined,
  RestaurantSectorType.bar => Icons.local_bar_outlined,
  RestaurantSectorType.vip => Icons.workspace_premium_outlined,
  RestaurantSectorType.counter => Icons.countertops_outlined,
  RestaurantSectorType.other => Icons.place_outlined,
};
String _typeLabel(RestaurantSectorType type) => switch (type) {
  RestaurantSectorType.diningRoom => 'Salão',
  RestaurantSectorType.outdoor => 'Área externa',
  RestaurantSectorType.bar => 'Bar',
  RestaurantSectorType.vip => 'Área VIP',
  RestaurantSectorType.counter => 'Balcão',
  RestaurantSectorType.other => 'Outro',
};
