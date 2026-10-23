import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../core/localization/app_strings.dart';
import '../data/restaurant_public_menu_remote_data_source.dart';
import '../domain/restaurant_public_menu.dart';

class RestaurantOnlineMenuScreen extends ConsumerStatefulWidget {
  const RestaurantOnlineMenuScreen({required this.qrCode, super.key});

  final String qrCode;

  @override
  ConsumerState<RestaurantOnlineMenuScreen> createState() =>
      _RestaurantOnlineMenuScreenState();
}

class _RestaurantOnlineMenuScreenState
    extends ConsumerState<RestaurantOnlineMenuScreen> {
  final _searchController = TextEditingController();
  String _selectedPeriod = 'all';
  String _search = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final strings = ref.watch(appStringsProvider);
    if (widget.qrCode.isEmpty) {
      return _messageScreen(strings.invalidMenuLink);
    }

    final menu = ref.watch(restaurantPublicMenuProvider(widget.qrCode));
    return Scaffold(
      backgroundColor: const Color(0xFFF6F7F5),
      body: menu.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => _loadError(strings),
        data: (value) => _menuPage(context, strings, value),
      ),
    );
  }

  Widget _menuPage(
    BuildContext context,
    AppStrings strings,
    RestaurantPublicMenu menu,
  ) {
    final periods = menu.items.map((item) => item.servicePeriod).toSet();
    final visibleItems = menu.items.where((item) {
      final matchesPeriod =
          _selectedPeriod == 'all' || item.servicePeriod == _selectedPeriod;
      final query = _search.trim().toLowerCase();
      final matchesSearch =
          query.isEmpty ||
          item.name.toLowerCase().contains(query) ||
          (item.description?.toLowerCase().contains(query) ?? false);
      return matchesPeriod && matchesSearch;
    }).toList();
    final locale = strings.isPortuguese ? 'pt_BR' : 'en_US';
    final priceFormat = NumberFormat.simpleCurrency(
      name: menu.currency,
      locale: locale,
    );

    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () async {
          await ref
              .refresh(restaurantPublicMenuProvider(widget.qrCode).future)
              .then<void>((_) {});
        },
        child: ListView(
          padding: const EdgeInsets.only(bottom: AppSpacing.xl),
          children: [
            _MenuHero(
              restaurantName: menu.restaurantName,
              tableLabel: strings.tableName(menu.tableNumber),
              subtitle: strings.onlineMenuSubtitle,
            ),
            Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 1120),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.lg),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        strings.onlineMenu,
                        style: Theme.of(context).textTheme.headlineMedium
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: AppSpacing.md),
                      TextField(
                        controller: _searchController,
                        onChanged: (value) => setState(() => _search = value),
                        decoration: InputDecoration(
                          hintText: strings.menuSearchHint,
                          prefixIcon: const Icon(Icons.search),
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(16),
                            borderSide: BorderSide.none,
                          ),
                        ),
                      ),
                      const SizedBox(height: AppSpacing.md),
                      Wrap(
                        spacing: AppSpacing.sm,
                        runSpacing: AppSpacing.sm,
                        children: [
                          _periodChip(strings.allPeriods, 'all'),
                          for (final period in periods)
                            _periodChip(_periodLabel(period, strings), period),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.lg),
                      if (visibleItems.isEmpty)
                        _EmptyMenu(message: strings.onlineMenuEmpty)
                      else
                        LayoutBuilder(
                          builder: (context, constraints) {
                            final columns = constraints.maxWidth >= 820
                                ? 3
                                : constraints.maxWidth >= 560
                                ? 2
                                : 1;
                            final spacing = AppSpacing.md;
                            final cardWidth =
                                (constraints.maxWidth -
                                    spacing * (columns - 1)) /
                                columns;
                            return Wrap(
                              spacing: spacing,
                              runSpacing: spacing,
                              children: [
                                for (final item in visibleItems)
                                  SizedBox(
                                    width: cardWidth,
                                    child: _MenuItemCard(
                                      item: item,
                                      price: priceFormat.format(
                                        double.parse(item.salePrice),
                                      ),
                                      period: _periodLabel(
                                        item.servicePeriod,
                                        strings,
                                      ),
                                      noDescriptionLabel:
                                          strings.noItemDescription,
                                      soldOutLabel: strings.soldOut,
                                    ),
                                  ),
                              ],
                            );
                          },
                        ),
                      const SizedBox(height: AppSpacing.lg),
                      _OrderNotice(message: strings.onlineMenuNotice),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _periodChip(String label, String value) => FilterChip(
    label: Text(label),
    selected: _selectedPeriod == value,
    onSelected: (_) => setState(() => _selectedPeriod = value),
    selectedColor: AppColors.brand.withValues(alpha: .12),
    checkmarkColor: AppColors.brand,
  );

  String _periodLabel(String period, AppStrings strings) => switch (period) {
    'lunch' => strings.lunch,
    'dinner' => strings.dinner,
    'all_day' => strings.allDay,
    _ => period,
  };

  Widget _loadError(AppStrings strings) => Center(
    child: Padding(
      padding: const EdgeInsets.all(AppSpacing.xl),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.restaurant_menu_outlined, size: 48),
          const SizedBox(height: AppSpacing.md),
          Text(strings.unableToLoadMenu, textAlign: TextAlign.center),
          const SizedBox(height: AppSpacing.md),
          FilledButton.icon(
            onPressed: () =>
                ref.invalidate(restaurantPublicMenuProvider(widget.qrCode)),
            icon: const Icon(Icons.refresh),
            label: Text(strings.tryAgain),
          ),
        ],
      ),
    ),
  );

  Widget _messageScreen(String message) => Scaffold(
    backgroundColor: const Color(0xFFF6F7F5),
    body: Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Text(message, textAlign: TextAlign.center),
      ),
    ),
  );
}

class _MenuHero extends StatelessWidget {
  const _MenuHero({
    required this.restaurantName,
    required this.tableLabel,
    required this.subtitle,
  });

  final String restaurantName;
  final String tableLabel;
  final String subtitle;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(
      AppSpacing.lg,
      AppSpacing.xl,
      AppSpacing.lg,
      AppSpacing.lg,
    ),
    decoration: const BoxDecoration(
      gradient: LinearGradient(
        colors: [Color(0xFF173B38), Color(0xFF23675A)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
    ),
    child: Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1120),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.restaurant, color: Color(0xFFC8F169), size: 32),
            const SizedBox(height: AppSpacing.md),
            Text(
              restaurantName,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(subtitle, style: const TextStyle(color: Colors.white70)),
            const SizedBox(height: AppSpacing.md),
            DecoratedBox(
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: .14),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.md,
                  vertical: AppSpacing.xs,
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.table_restaurant_outlined,
                      color: Color(0xFFC8F169),
                      size: 18,
                    ),
                    const SizedBox(width: AppSpacing.xs),
                    Text(
                      tableLabel,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

class _MenuItemCard extends StatelessWidget {
  const _MenuItemCard({
    required this.item,
    required this.price,
    required this.period,
    required this.noDescriptionLabel,
    required this.soldOutLabel,
  });

  final RestaurantPublicMenuItem item;
  final String price;
  final String period;
  final String noDescriptionLabel;
  final String soldOutLabel;

  @override
  Widget build(BuildContext context) => Card(
    clipBehavior: Clip.antiAlias,
    elevation: 1,
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        AspectRatio(
          aspectRatio: 16 / 10,
          child: item.imageUrl == null || item.imageUrl!.isEmpty
              ? const _ImagePlaceholder()
              : Image.network(
                  item.imageUrl!,
                  fit: BoxFit.cover,
                  errorBuilder: (_, _, _) => const _ImagePlaceholder(),
                ),
        ),
        Padding(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      item.name,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  if (!item.isAvailable) _AvailabilityTag(label: soldOutLabel),
                ],
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                item.description?.isNotEmpty == true
                    ? item.description!
                    : noDescriptionLabel,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF667085),
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    period,
                    style: Theme.of(
                      context,
                    ).textTheme.labelLarge?.copyWith(color: AppColors.brand),
                  ),
                  Text(
                    price,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: AppColors.brand,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class _ImagePlaceholder extends StatelessWidget {
  const _ImagePlaceholder();

  @override
  Widget build(BuildContext context) => const ColoredBox(
    color: Color(0xFFE7ECE9),
    child: Center(
      child: Icon(
        Icons.restaurant_menu_outlined,
        size: 44,
        color: Color(0xFF5C716A),
      ),
    ),
  );
}

class _AvailabilityTag extends StatelessWidget {
  const _AvailabilityTag({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) => DecoratedBox(
    decoration: BoxDecoration(
      color: const Color(0xFFFFE6DF),
      borderRadius: BorderRadius.circular(20),
    ),
    child: Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.sm,
        vertical: AppSpacing.xs,
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Color(0xFF9A3412),
          fontWeight: FontWeight.w700,
        ),
      ),
    ),
  );
}

class _EmptyMenu extends StatelessWidget {
  const _EmptyMenu({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(AppSpacing.xl),
      child: Center(
        child: Column(
          children: [
            const Icon(
              Icons.menu_book_outlined,
              size: 40,
              color: AppColors.brand,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(message, textAlign: TextAlign.center),
          ],
        ),
      ),
    ),
  );
}

class _OrderNotice extends StatelessWidget {
  const _OrderNotice({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(AppSpacing.md),
    decoration: BoxDecoration(
      color: const Color(0xFFE8F1EF),
      borderRadius: BorderRadius.circular(16),
    ),
    child: Row(
      children: [
        const Icon(Icons.info_outline, color: AppColors.brand),
        const SizedBox(width: AppSpacing.sm),
        Expanded(child: Text(message)),
      ],
    ),
  );
}
