import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../data/restaurant_sector_remote_data_source.dart';
import '../data/restaurant_staff_remote_data_source.dart';

class RestaurantStaffScreen extends ConsumerWidget {
  const RestaurantStaffScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final staff = ref.watch(restaurantStaffProvider);
    final sectors = ref.watch(restaurantSectorsProvider).asData?.value ?? [];
    return AppScaffold(
      title: 'Garçons e equipe',
      body: staff.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) =>
            const Center(child: Text('Não foi possível carregar a equipe.')),
        data: (items) {
          final serving = items
              .where((item) => item.status == 'serving')
              .length;
          final paused = items.where((item) => item.status == 'paused').length;
          final sectorName = {
            for (final sector in sectors) sector.id: sector.name,
          };
          return ListView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            children: [
              _Header(onCreate: () => _createStaff(context, ref)),
              const SizedBox(height: AppSpacing.lg),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  _Metric(
                    'Profissionais',
                    '${items.length}',
                    'Total cadastrados',
                    Icons.groups_outlined,
                    AppColors.brand,
                  ),
                  _Metric(
                    'Em atendimento',
                    '$serving',
                    '${_percentage(serving, items.length)}% da equipe',
                    Icons.person_outline,
                    AppColors.success,
                  ),
                  _Metric(
                    'Setores cobertos',
                    '${items.where((item) => item.sectorId != null).map((item) => item.sectorId).toSet().length}',
                    'Com equipe ativa',
                    Icons.storefront_outlined,
                    AppColors.brand,
                  ),
                  _Metric(
                    'Em pausa',
                    '$paused',
                    '${_percentage(paused, items.length)}% da equipe',
                    Icons.pause_circle_outline,
                    AppColors.warning,
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              LayoutBuilder(
                builder: (context, constraints) => constraints.maxWidth >= 900
                    ? _Desktop(items: items, sectorName: sectorName)
                    : _Mobile(items: items, sectorName: sectorName),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.onCreate});
  final VoidCallback onCreate;
  @override
  Widget build(BuildContext context) => Row(
    children: [
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Restaurante  >  Garçons e equipe',
              style: TextStyle(color: AppColors.brand),
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Garçons e equipe',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Organize a equipe de atendimento e acompanhe a operação por setor.',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
      OutlinedButton.icon(
        onPressed: onCreate,
        icon: const Icon(Icons.add_circle_outline),
        label: const Text('Novo garçom'),
      ),
    ],
  );
}

class _Metric extends StatelessWidget {
  const _Metric(this.label, this.value, this.detail, this.icon, this.color);
  final String label, value, detail;
  final IconData icon;
  final Color color;
  @override
  Widget build(BuildContext context) => SizedBox(
    width: 250,
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.md),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: color.withValues(alpha: .12),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: AppSpacing.md),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(value, style: Theme.of(context).textTheme.titleLarge),
                Text(label, style: Theme.of(context).textTheme.titleMedium),
                Text(detail, style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}

class _Desktop extends StatelessWidget {
  const _Desktop({required this.items, required this.sectorName});
  final List<RestaurantStaff> items;
  final Map<String, String> sectorName;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Wrap(
        spacing: AppSpacing.md,
        runSpacing: AppSpacing.md,
        children: items
            .take(4)
            .map(
              (item) => SizedBox(
                width: 260,
                child: _StaffCard(
                  item: item,
                  sectorName: sectorName[item.sectorId] ?? 'Sem setor',
                ),
              ),
            )
            .toList(),
      ),
      const SizedBox(height: AppSpacing.lg),
      Card(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(AppSpacing.md),
              child: Row(
                children: [
                  Text(
                    'Equipe operacional',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const Spacer(),
                  const SizedBox(
                    width: 250,
                    child: TextField(
                      decoration: InputDecoration(
                        prefixIcon: Icon(Icons.search),
                        hintText: 'Buscar profissional...',
                      ),
                    ),
                  ),
                ],
              ),
            ),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('Profissional')),
                  DataColumn(label: Text('Função')),
                  DataColumn(label: Text('Setor atual')),
                  DataColumn(label: Text('Status')),
                  DataColumn(label: Text('Ações')),
                ],
                rows: items
                    .map(
                      (item) => DataRow(
                        cells: [
                          DataCell(Text(item.name)),
                          DataCell(Text(_role(item.role))),
                          DataCell(
                            Text(sectorName[item.sectorId] ?? 'Sem setor'),
                          ),
                          DataCell(_Status(item.status)),
                          DataCell(const Icon(Icons.more_vert)),
                        ],
                      ),
                    )
                    .toList(),
              ),
            ),
          ],
        ),
      ),
    ],
  );
}

class _Mobile extends StatelessWidget {
  const _Mobile({required this.items, required this.sectorName});
  final List<RestaurantStaff> items;
  final Map<String, String> sectorName;
  @override
  Widget build(BuildContext context) => Column(
    children: items
        .map(
          (item) => Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.sm),
            child: _StaffCard(
              item: item,
              sectorName: sectorName[item.sectorId] ?? 'Sem setor',
            ),
          ),
        )
        .toList(),
  );
}

class _StaffCard extends StatelessWidget {
  const _StaffCard({required this.item, required this.sectorName});
  final RestaurantStaff item;
  final String sectorName;
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
                backgroundColor: AppColors.brand.withValues(alpha: .12),
                child: Text(
                  _initials(item.name),
                  style: const TextStyle(color: AppColors.brand),
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.name,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    Text(_role(item.role)),
                  ],
                ),
              ),
              const Icon(Icons.more_vert),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Text(sectorName, style: Theme.of(context).textTheme.titleSmall),
          const Text('Setor atual'),
          const SizedBox(height: AppSpacing.md),
          _Status(item.status),
        ],
      ),
    ),
  );
}

class _Status extends StatelessWidget {
  const _Status(this.status);
  final String status;
  @override
  Widget build(BuildContext context) {
    final paused = status == 'paused';
    return Chip(
      avatar: Icon(
        Icons.circle,
        size: 10,
        color: paused ? AppColors.warning : AppColors.success,
      ),
      label: Text(
        paused
            ? 'Em pausa'
            : status == 'serving'
            ? 'Em atendimento'
            : 'Disponível',
      ),
    );
  }
}

String _role(String value) => switch (value) {
  'waiter' => 'Garçom',
  'attendant' => 'Atendente',
  'manager' => 'Gerente',
  _ => value,
};
String _initials(String name) =>
    name.split(' ').take(2).map((word) => word[0]).join();
int _percentage(int value, int total) =>
    total == 0 ? 0 : (value * 100 / total).round();
Future<void> _createStaff(BuildContext context, WidgetRef ref) async {
  final name = TextEditingController();
  final code = TextEditingController();
  final save = await showDialog<bool>(
    context: context,
    builder: (dialogContext) => AlertDialog(
      title: const Text('Novo garçom'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: name,
            decoration: const InputDecoration(labelText: 'Nome'),
          ),
          const SizedBox(height: AppSpacing.md),
          TextField(
            controller: code,
            decoration: const InputDecoration(labelText: 'Código'),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(dialogContext),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: () => Navigator.pop(dialogContext, true),
          child: const Text('Salvar'),
        ),
      ],
    ),
  );
  if (save != true || name.text.trim().isEmpty || code.text.trim().isEmpty) {
    return;
  }
  try {
    await ref
        .read(restaurantStaffRemoteDataSourceProvider)
        .create(code: code.text.trim().toUpperCase(), name: name.text.trim());
    ref.invalidate(restaurantStaffProvider);
  } catch (_) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Não foi possível salvar o profissional.'),
        ),
      );
    }
  } finally {
    name.dispose();
    code.dispose();
  }
}
