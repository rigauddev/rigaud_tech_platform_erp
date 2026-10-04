import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../../app/config/app_config.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../data/restaurant_remote_data_source.dart';
import '../domain/restaurant_table.dart';
import 'restaurant_tables_controller.dart';

class RestaurantTableQrCodesScreen extends ConsumerStatefulWidget {
  const RestaurantTableQrCodesScreen({super.key});

  @override
  ConsumerState<RestaurantTableQrCodesScreen> createState() =>
      _RestaurantTableQrCodesScreenState();
}

class _RestaurantTableQrCodesScreenState
    extends ConsumerState<RestaurantTableQrCodesScreen> {
  final _search = TextEditingController();
  final _selectedIds = <String>{};
  bool _showCompanyName = true;

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final strings = ref.watch(appStringsProvider);
    final tables = ref.watch(restaurantTablesProvider(null));
    final floors =
        ref.watch(restaurantFloorsProvider).asData?.value ?? const [];
    final floorNames = {for (final floor in floors) floor.id: floor.name};

    return AppScaffold(
      title: strings.tableQrCodes,
      body: tables.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: OutlinedButton.icon(
            onPressed: () => ref.invalidate(restaurantTablesProvider(null)),
            icon: const Icon(Icons.refresh_outlined),
            label: Text(strings.tryAgain),
          ),
        ),
        data: (items) {
          if (items.isEmpty) {
            return const AppEmptyState(
              title: 'Nenhuma mesa cadastrada',
              message: 'Cadastre mesas antes de gerar os QR Codes de acesso.',
            );
          }
          final query = _search.text.trim().toLowerCase();
          final filtered = items
              .where(
                (table) =>
                    query.isEmpty ||
                    table.number.toLowerCase().contains(query) ||
                    (table.name?.toLowerCase().contains(query) ?? false),
              )
              .toList();
          final active = items.where((item) => item.isActive).toList();
          final withQr = active.where((item) => item.qrCode != null).length;
          final withoutQr = active.length - withQr;
          final disabled = items.where((item) => !item.isActive).length;

          return ListView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            children: [
              _Header(onGenerate: () => _generateMissing(active)),
              const SizedBox(height: AppSpacing.lg),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  _Metric(
                    'Mesas ativas',
                    '${active.length}',
                    Icons.table_restaurant_outlined,
                    AppColors.brand,
                  ),
                  _Metric(
                    'QR ativos',
                    '$withQr',
                    Icons.qr_code_2_outlined,
                    AppColors.success,
                  ),
                  _Metric(
                    'Sem QR',
                    '$withoutQr',
                    Icons.warning_amber_outlined,
                    AppColors.warning,
                  ),
                  _Metric(
                    'Desativadas',
                    '$disabled',
                    Icons.block_outlined,
                    AppColors.error,
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              LayoutBuilder(
                builder: (context, constraints) {
                  final wide = constraints.maxWidth >= 1100;
                  final access = _AccessByTable(
                    items: filtered,
                    selectedIds: _selectedIds,
                    onToggle: _toggle,
                    onGenerate: _generate,
                  );
                  final print = _PrintSecurity(
                    showCompanyName: _showCompanyName,
                    onChanged: (value) =>
                        setState(() => _showCompanyName = value),
                    hasSelection: _selectedIds.isNotEmpty,
                    onPrint: _printSelected,
                  );
                  return wide
                      ? Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(child: access),
                            const SizedBox(width: AppSpacing.md),
                            SizedBox(width: 332, child: print),
                          ],
                        )
                      : Column(
                          children: [
                            access,
                            const SizedBox(height: AppSpacing.md),
                            print,
                          ],
                        );
                },
              ),
              const SizedBox(height: AppSpacing.lg),
              _QrControlTable(
                items: filtered,
                floorNames: floorNames,
                selectedIds: _selectedIds,
                search: _search,
                onSearch: () => setState(() {}),
                onToggle: _toggle,
                onGenerate: _generate,
                onPrint: _printTable,
              ),
            ],
          );
        },
      ),
    );
  }

  Future<void> _generateMissing(List<RestaurantTable> tables) async {
    for (final table in tables.where((item) => item.qrCode == null)) {
      await _generate(table, silent: true);
    }
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('QR Codes gerados para as mesas pendentes.'),
        ),
      );
    }
  }

  Future<void> _generate(RestaurantTable table, {bool silent = false}) async {
    await ref.read(restaurantRemoteDataSourceProvider).generateQrCode(table.id);
    ref.invalidate(restaurantTablesProvider(null));
    if (!silent && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('QR Code da Mesa ${table.number} renovado.')),
      );
    }
  }

  void _toggle(String id, bool selected) => setState(() {
    selected ? _selectedIds.add(id) : _selectedIds.remove(id);
  });

  void _printSelected() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '${_selectedIds.length} QR Code(s) preparado(s) para impressão.',
        ),
      ),
    );
  }

  void _printTable(RestaurantTable table) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'QR Code da Mesa ${table.number} preparado para impressão.',
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.onGenerate});
  final VoidCallback onGenerate;
  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Restaurante  >  QR Codes das mesas',
              style: const TextStyle(
                color: AppColors.brand,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'QR Codes das mesas',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Gere, imprima e gerencie o acesso digital de cada mesa.',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
      OutlinedButton.icon(
        onPressed: onGenerate,
        icon: const Icon(Icons.qr_code_2_outlined),
        label: const Text('Gerar QR Codes'),
      ),
    ],
  );
}

class _Metric extends StatelessWidget {
  const _Metric(this.label, this.value, this.icon, this.color);
  final String label;
  final String value;
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
              ],
            ),
          ],
        ),
      ),
    ),
  );
}

class _AccessByTable extends StatelessWidget {
  const _AccessByTable({
    required this.items,
    required this.selectedIds,
    required this.onToggle,
    required this.onGenerate,
  });
  final List<RestaurantTable> items;
  final Set<String> selectedIds;
  final void Function(String, bool) onToggle;
  final Future<void> Function(RestaurantTable) onGenerate;
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Acesso por mesa',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: AppSpacing.md),
          Wrap(
            spacing: AppSpacing.md,
            runSpacing: AppSpacing.md,
            children: items
                .take(6)
                .map(
                  (table) => _QrCard(
                    table: table,
                    selected: selectedIds.contains(table.id),
                    onToggle: onToggle,
                    onGenerate: onGenerate,
                  ),
                )
                .toList(),
          ),
        ],
      ),
    ),
  );
}

class _QrCard extends StatelessWidget {
  const _QrCard({
    required this.table,
    required this.selected,
    required this.onToggle,
    required this.onGenerate,
  });
  final RestaurantTable table;
  final bool selected;
  final void Function(String, bool) onToggle;
  final Future<void> Function(RestaurantTable) onGenerate;
  @override
  Widget build(BuildContext context) {
    final token = table.qrCode;
    return SizedBox(
      width: 170,
      child: DecoratedBox(
        decoration: BoxDecoration(
          border: Border.all(color: const Color(0xFFE1E8F3)),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.sm),
          child: Column(
            children: [
              Row(
                children: [
                  Checkbox(
                    value: selected,
                    onChanged: (value) => onToggle(table.id, value ?? false),
                  ),
                  Expanded(
                    child: Text(
                      'Mesa ${table.number}',
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ),
                  PopupMenuButton<String>(
                    onSelected: (_) => onGenerate(table),
                    itemBuilder: (_) => const [
                      PopupMenuItem(
                        value: 'renew',
                        child: Text('Renovar QR Code'),
                      ),
                    ],
                  ),
                ],
              ),
              SizedBox(
                height: 96,
                child: token == null
                    ? const Icon(
                        Icons.qr_code_2_outlined,
                        size: 76,
                        color: Color(0xFF98A2B3),
                      )
                    : QrImageView(
                        data: _qrData(token),
                        size: 96,
                        padding: EdgeInsets.zero,
                      ),
              ),
              const SizedBox(height: AppSpacing.xs),
              _StatusChip(active: token != null && table.isActive),
            ],
          ),
        ),
      ),
    );
  }
}

class _PrintSecurity extends StatelessWidget {
  const _PrintSecurity({
    required this.showCompanyName,
    required this.onChanged,
    required this.hasSelection,
    required this.onPrint,
  });
  final bool showCompanyName;
  final ValueChanged<bool> onChanged;
  final bool hasSelection;
  final VoidCallback onPrint;
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Impressão e segurança',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: AppSpacing.md),
          DropdownButtonFormField<String>(
            initialValue: 'a4',
            decoration: const InputDecoration(
              labelText: 'Formato de impressão',
              prefixIcon: Icon(Icons.print_outlined),
            ),
            items: const [
              DropdownMenuItem(
                value: 'a4',
                child: Text('Folha A4 com 6 códigos'),
              ),
            ],
            onChanged: (_) {},
          ),
          const SizedBox(height: AppSpacing.sm),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Exibir nome da empresa'),
            value: showCompanyName,
            onChanged: onChanged,
          ),
          const SizedBox(height: AppSpacing.sm),
          Container(
            padding: const EdgeInsets.all(AppSpacing.sm),
            decoration: BoxDecoration(
              color: const Color(0xFFEAF2FF),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.info_outline, color: AppColors.brand),
                SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: Text(
                    'O QR Code identifica a mesa e poderá abrir o cardápio digital quando ele estiver disponível. Renovar o código invalida o anterior.',
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          FilledButton.icon(
            onPressed: hasSelection ? onPrint : null,
            icon: const Icon(Icons.print_outlined),
            label: const Text('Imprimir selecionados'),
          ),
        ],
      ),
    ),
  );
}

class _QrControlTable extends StatelessWidget {
  const _QrControlTable({
    required this.items,
    required this.floorNames,
    required this.selectedIds,
    required this.search,
    required this.onSearch,
    required this.onToggle,
    required this.onGenerate,
    required this.onPrint,
  });
  final List<RestaurantTable> items;
  final Map<String, String> floorNames;
  final Set<String> selectedIds;
  final TextEditingController search;
  final VoidCallback onSearch;
  final void Function(String, bool) onToggle;
  final Future<void> Function(RestaurantTable) onGenerate;
  final ValueChanged<RestaurantTable> onPrint;
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(AppSpacing.md),
            child: Row(
              children: [
                Text(
                  'Controle de QR Codes',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const Spacer(),
                SizedBox(
                  width: 250,
                  child: TextField(
                    controller: search,
                    onChanged: (_) => onSearch(),
                    decoration: const InputDecoration(
                      hintText: 'Buscar mesa...',
                      prefixIcon: Icon(Icons.search_outlined),
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
                DataColumn(label: Text('')),
                DataColumn(label: Text('Mesa')),
                DataColumn(label: Text('Setor / Ambiente')),
                DataColumn(label: Text('Status')),
                DataColumn(label: Text('Ações')),
              ],
              rows: items.map((table) {
                return DataRow(
                  cells: [
                    DataCell(
                      Checkbox(
                        value: selectedIds.contains(table.id),
                        onChanged: (value) =>
                            onToggle(table.id, value ?? false),
                      ),
                    ),
                    DataCell(
                      Text(
                        'Mesa ${table.number}',
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ),
                    DataCell(Text(floorNames[table.floorId] ?? 'Salão')),
                    DataCell(
                      _StatusChip(
                        active: table.qrCode != null && table.isActive,
                      ),
                    ),
                    DataCell(
                      Row(
                        children: [
                          IconButton(
                            tooltip: 'Visualizar QR Code',
                            onPressed: table.qrCode == null
                                ? null
                                : () => _showQr(context, table),
                            icon: const Icon(Icons.visibility_outlined),
                          ),
                          IconButton(
                            tooltip: 'Renovar QR Code',
                            onPressed: () => onGenerate(table),
                            icon: const Icon(Icons.refresh_outlined),
                          ),
                          IconButton(
                            tooltip: 'Imprimir QR Code',
                            onPressed: table.qrCode == null
                                ? null
                                : () => onPrint(table),
                            icon: const Icon(Icons.print_outlined),
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  void _showQr(BuildContext context, RestaurantTable table) => showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Mesa ${table.number}'),
      content: QrImageView(data: _qrData(table.qrCode!), size: 220),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Fechar'),
        ),
      ],
    ),
  );
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.active});
  final bool active;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
    decoration: BoxDecoration(
      color: (active ? AppColors.success : AppColors.warning).withValues(
        alpha: .12,
      ),
      borderRadius: BorderRadius.circular(16),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.circle,
          size: 8,
          color: active ? AppColors.success : AppColors.warning,
        ),
        const SizedBox(width: 6),
        Text(
          active ? 'Ativo' : 'Sem QR',
          style: TextStyle(
            color: active ? AppColors.success : AppColors.warning,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    ),
  );
}

String _qrData(String token) =>
    '${AppConfig.fromEnvironment().apiBaseUrl}/api/v1/restaurant/table-access/$token';
