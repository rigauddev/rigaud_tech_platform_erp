import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../../products/data/product_remote_data_source.dart';
import '../../products/domain/product.dart';
import '../data/restaurant_menu_availability_remote_data_source.dart';

final _menuProductsProvider = FutureProvider<List<Product>>(
  (ref) => ref.watch(productRemoteDataSourceProvider).list(pageSize: 100),
);

class RestaurantMenuAvailabilityScreen extends ConsumerWidget {
  const RestaurantMenuAvailabilityScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = ref.watch(appStringsProvider);
    final availability = ref.watch(restaurantMenuAvailabilityProvider);
    final products = ref.watch(_menuProductsProvider).asData?.value ?? [];
    final productsById = {for (final product in products) product.id: product};

    return AppScaffold(
      title: strings.dailyMenu,
      body: availability.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) =>
            Center(child: Text(strings.unableToLoadMenu)),
        data: (items) {
          final published = items
              .where((item) => item.status == 'published')
              .length;
          final soldOut = items
              .where((item) => item.remainingQuantity == 0)
              .length;
          final limited = items.where((item) {
            final remaining = item.remainingQuantity;
            return remaining != null && remaining > 0 && remaining <= 6;
          }).length;
          return ListView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            children: [
              _Header(
                strings: strings,
                onAdd: () => _createItem(context, ref, products, strings),
              ),
              const SizedBox(height: AppSpacing.md),
              _Filters(strings: strings),
              const SizedBox(height: AppSpacing.md),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  _Metric(
                    strings.publishedItems,
                    '$published',
                    Icons.list_alt_outlined,
                    AppColors.brand,
                  ),
                  _Metric(
                    strings.availableItems,
                    '${published - soldOut}',
                    Icons.check_circle_outline,
                    AppColors.success,
                  ),
                  _Metric(
                    strings.limitedQuota,
                    '$limited',
                    Icons.timelapse_outlined,
                    AppColors.warning,
                  ),
                  _Metric(
                    strings.unavailableItems,
                    '$soldOut',
                    Icons.block_outlined,
                    const Color(0xFF667085),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              _AvailabilityTable(
                items: items,
                products: productsById,
                strings: strings,
              ),
            ],
          );
        },
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.strings, required this.onAdd});
  final AppStrings strings;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) => Wrap(
      alignment: WrapAlignment.spaceBetween,
      runSpacing: AppSpacing.md,
      children: [
        SizedBox(
          width: constraints.maxWidth > 660
              ? constraints.maxWidth - 180
              : constraints.maxWidth,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Restaurante  >  ${strings.menu}',
                style: const TextStyle(color: AppColors.brand),
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                strings.dailyMenu,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                strings.menuAvailabilityDescription,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ],
          ),
        ),
        FilledButton.icon(
          onPressed: onAdd,
          icon: const Icon(Icons.add),
          label: Text(strings.addItem),
        ),
      ],
    ),
  );
}

class _Filters extends StatelessWidget {
  const _Filters({required this.strings});

  final AppStrings strings;
  @override
  Widget build(BuildContext context) => Wrap(
    spacing: AppSpacing.sm,
    runSpacing: AppSpacing.sm,
    children: [
      _Filter(label: strings.today),
      _Filter(label: strings.lunch),
      _Filter(label: strings.allChannels),
    ],
  );
}

class _Filter extends StatelessWidget {
  const _Filter({required this.label});
  final String label;
  @override
  Widget build(BuildContext context) => OutlinedButton.icon(
    onPressed: () {},
    icon: const Icon(Icons.keyboard_arrow_down, size: 18),
    label: Text(label),
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

class _AvailabilityTable extends StatelessWidget {
  const _AvailabilityTable({
    required this.items,
    required this.products,
    required this.strings,
  });
  final List<RestaurantMenuAvailability> items;
  final Map<String, Product> products;
  final AppStrings strings;

  @override
  Widget build(BuildContext context) => Card(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  strings.commercialAvailability,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              SizedBox(
                width: 240,
                child: TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.search),
                    hintText: strings.searchItem,
                  ),
                ),
              ),
            ],
          ),
        ),
        if (items.isEmpty)
          Padding(
            padding: const EdgeInsets.all(AppSpacing.xl),
            child: Center(child: Text(strings.noMenuItems)),
          )
        else
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columns: [
                DataColumn(label: Text(strings.products.toUpperCase())),
                DataColumn(label: Text(strings.channels.toUpperCase())),
                DataColumn(label: Text(strings.dailyQuota.toUpperCase())),
                DataColumn(label: Text(strings.remaining.toUpperCase())),
                DataColumn(label: Text(strings.status.toUpperCase())),
              ],
              rows: items
                  .map(
                    (item) => DataRow(
                      cells: [
                        DataCell(
                          Text(
                            products[item.productId]?.name ?? item.productId,
                          ),
                        ),
                        DataCell(Text(item.channels.join(', '))),
                        DataCell(
                          Text(
                            item.availableQuantity?.toString() ??
                                strings.unlimited,
                          ),
                        ),
                        DataCell(
                          Text(
                            item.remainingQuantity?.toString() ??
                                strings.unlimited,
                          ),
                        ),
                        DataCell(_StatusChip(item: item, strings: strings)),
                      ],
                    ),
                  )
                  .toList(),
            ),
          ),
      ],
    ),
  );
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.item, required this.strings});
  final RestaurantMenuAvailability item;
  final AppStrings strings;
  @override
  Widget build(BuildContext context) {
    final soldOut = item.remainingQuantity == 0;
    final limited =
        !soldOut &&
        item.remainingQuantity != null &&
        item.remainingQuantity! <= 6;
    final color = soldOut
        ? const Color(0xFF667085)
        : limited
        ? AppColors.warning
        : AppColors.success;
    final label = soldOut
        ? strings.soldOut
        : limited
        ? strings.limitedQuota
        : strings.availableItems;
    return Chip(
      avatar: Icon(Icons.circle, size: 9, color: color),
      label: Text(label),
    );
  }
}

Future<void> _createItem(
  BuildContext context,
  WidgetRef ref,
  List<Product> products,
  AppStrings strings,
) async {
  String? productId;
  final quantity = TextEditingController();
  final saved = await showDialog<bool>(
    context: context,
    builder: (dialogContext) => StatefulBuilder(
      builder: (context, setState) => AlertDialog(
        title: Text(strings.addItem),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            DropdownButtonFormField<String>(
              initialValue: productId,
              decoration: InputDecoration(labelText: strings.products),
              items: products
                  .where((product) => product.isActive)
                  .map(
                    (product) => DropdownMenuItem(
                      value: product.id,
                      child: Text(product.name),
                    ),
                  )
                  .toList(),
              onChanged: (value) => setState(() => productId = value),
            ),
            const SizedBox(height: AppSpacing.md),
            TextField(
              controller: quantity,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: strings.dailyQuota,
                hintText: strings.unlimited,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: Text(strings.cancel),
          ),
          FilledButton(
            onPressed: productId == null
                ? null
                : () => Navigator.pop(dialogContext, true),
            child: Text(strings.save),
          ),
        ],
      ),
    ),
  );
  if (saved == true && productId != null) {
    await ref
        .read(restaurantMenuAvailabilityRemoteDataSourceProvider)
        .create(
          productId: productId!,
          serviceDate: DateTime.now(),
          servicePeriod: 'lunch',
          channels: const ['dining_room', 'qr'],
          availableQuantity: int.tryParse(quantity.text),
        );
    ref.invalidate(restaurantMenuAvailabilityProvider);
  }
  quantity.dispose();
}
