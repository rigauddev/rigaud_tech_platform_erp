import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../data/restaurant_sector_remote_data_source.dart';
import '../data/restaurant_staff_remote_data_source.dart';

class RestaurantStaffScreen extends ConsumerWidget {
  const RestaurantStaffScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final staff = ref.watch(restaurantStaffProvider);
    final sectors = ref.watch(restaurantSectorsProvider).asData?.value ?? [];
    final strings = ref.watch(appStringsProvider);
    return AppScaffold(
      title: 'Garçons e equipe',
      body: staff.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(strings.unableToLoadStaff),
              const SizedBox(height: AppSpacing.sm),
              OutlinedButton.icon(
                onPressed: () => ref.invalidate(restaurantStaffProvider),
                icon: const Icon(Icons.refresh_outlined),
                label: Text(strings.tryAgain),
              ),
            ],
          ),
        ),
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
              _Header(
                strings: strings,
                onCreate: () => _createStaff(context, ref, strings),
              ),
              const SizedBox(height: AppSpacing.lg),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  _Metric(
                    strings.professionals,
                    '${items.length}',
                    strings.totalRegistered,
                    Icons.groups_outlined,
                    AppColors.brand,
                  ),
                  _Metric(
                    strings.serving,
                    '$serving',
                    '${_percentage(serving, items.length)}% ${strings.teamLabel}',
                    Icons.person_outline,
                    AppColors.success,
                  ),
                  _Metric(
                    strings.sectorsCovered,
                    '${items.where((item) => item.sectorId != null).map((item) => item.sectorId).toSet().length}',
                    strings.activeTeam,
                    Icons.storefront_outlined,
                    AppColors.brand,
                  ),
                  _Metric(
                    strings.paused,
                    '$paused',
                    '${_percentage(paused, items.length)}% ${strings.teamLabel}',
                    Icons.pause_circle_outline,
                    AppColors.warning,
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              LayoutBuilder(
                builder: (context, constraints) => constraints.maxWidth >= 900
                    ? _Desktop(
                        items: items,
                        sectorName: sectorName,
                        strings: strings,
                      )
                    : _Mobile(
                        items: items,
                        sectorName: sectorName,
                        strings: strings,
                      ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.onCreate, required this.strings});
  final VoidCallback onCreate;
  final AppStrings strings;
  @override
  Widget build(BuildContext context) => Row(
    children: [
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              strings.staffBreadcrumb,
              style: TextStyle(color: AppColors.brand),
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              strings.staffTitle,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              strings.staffDescription,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
      OutlinedButton.icon(
        onPressed: onCreate,
        icon: const Icon(Icons.add_circle_outline),
        label: Text(strings.newWaiter),
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
  const _Desktop({
    required this.items,
    required this.sectorName,
    required this.strings,
  });
  final List<RestaurantStaff> items;
  final Map<String, String> sectorName;
  final AppStrings strings;
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
                  sectorName: sectorName[item.sectorId] ?? strings.noSector,
                  strings: strings,
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
                    strings.operationalTeam,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const Spacer(),
                  SizedBox(
                    width: 250,
                    child: TextField(
                      decoration: InputDecoration(
                        prefixIcon: Icon(Icons.search),
                        hintText: strings.searchProfessional,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: [
                  DataColumn(label: Text(strings.professional)),
                  DataColumn(label: Text(strings.function)),
                  DataColumn(label: Text(strings.currentSector)),
                  DataColumn(label: Text(strings.status)),
                  DataColumn(label: Text(strings.actions)),
                ],
                rows: items
                    .map(
                      (item) => DataRow(
                        cells: [
                          DataCell(Text(item.name)),
                          DataCell(Text(_role(item.role, strings))),
                          DataCell(
                            Text(sectorName[item.sectorId] ?? strings.noSector),
                          ),
                          DataCell(_Status(item.status, strings)),
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
  const _Mobile({
    required this.items,
    required this.sectorName,
    required this.strings,
  });
  final List<RestaurantStaff> items;
  final Map<String, String> sectorName;
  final AppStrings strings;
  @override
  Widget build(BuildContext context) => Column(
    children: items
        .map(
          (item) => Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.sm),
            child: _StaffCard(
              item: item,
              sectorName: sectorName[item.sectorId] ?? strings.noSector,
              strings: strings,
            ),
          ),
        )
        .toList(),
  );
}

class _StaffCard extends StatelessWidget {
  const _StaffCard({
    required this.item,
    required this.sectorName,
    required this.strings,
  });
  final RestaurantStaff item;
  final String sectorName;
  final AppStrings strings;
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
                    Text(_role(item.role, strings)),
                  ],
                ),
              ),
              const Icon(Icons.more_vert),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Text(sectorName, style: Theme.of(context).textTheme.titleSmall),
          Text(strings.currentSector),
          const SizedBox(height: AppSpacing.md),
          _Status(item.status, strings),
        ],
      ),
    ),
  );
}

class _Status extends StatelessWidget {
  const _Status(this.status, this.strings);
  final String status;
  final AppStrings strings;
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
            ? strings.paused
            : status == 'serving'
            ? strings.serving
            : strings.available,
      ),
    );
  }
}

String _role(String value, AppStrings strings) => switch (value) {
  'waiter' => strings.waiter,
  'attendant' => strings.attendant,
  'manager' => strings.manager,
  _ => value,
};
String _initials(String name) =>
    name.split(' ').take(2).map((word) => word[0]).join();
int _percentage(int value, int total) =>
    total == 0 ? 0 : (value * 100 / total).round();
Future<void> _createStaff(
  BuildContext context,
  WidgetRef ref,
  AppStrings strings,
) async {
  final name = TextEditingController();
  final code = TextEditingController();
  final save = await showDialog<bool>(
    context: context,
    builder: (dialogContext) => AlertDialog(
      title: Text(strings.newWaiter),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: name,
            decoration: InputDecoration(labelText: strings.name),
          ),
          const SizedBox(height: AppSpacing.md),
          TextField(
            controller: code,
            decoration: InputDecoration(labelText: strings.code),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(dialogContext),
          child: Text(strings.cancel),
        ),
        FilledButton(
          onPressed: () => Navigator.pop(dialogContext, true),
          child: Text(strings.save),
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
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(strings.unableToSaveStaff)));
    }
  } finally {
    name.dispose();
    code.dispose();
  }
}
