import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/router/app_routes.dart';
import '../../app/theme/app_colors.dart';
import '../../core/localization/app_strings.dart';
import '../../features/auth/presentation/auth_controller.dart';

/// Shared frame for authenticated ERP screens.
/// The restaurant context remains expanded while its operational pages are used.
class AppScaffold extends ConsumerWidget {
  const AppScaffold({
    required this.body,
    this.title,
    this.selectedIndex = 0,
    this.actions,
    super.key,
  });

  final Widget body;
  final String? title;
  final int selectedIndex;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = ref.watch(appStringsProvider);
    final isDesktop = MediaQuery.sizeOf(context).width >= 1024;
    final currentPath = GoRouterState.of(context).uri.path;
    final parentRoute = _parentRouteFor(currentPath);
    final user = ref.watch(authControllerProvider).value?.user;
    final emailPrefix = user?.email.split('@').first.trim();
    final profileName = emailPrefix?.isNotEmpty == true
        ? emailPrefix!
        : 'Conta';

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 64,
        leading: parentRoute == null
            ? (isDesktop
                  ? null
                  : Builder(
                      builder: (context) => IconButton(
                        tooltip: strings.menu,
                        icon: const Icon(Icons.menu_outlined),
                        onPressed: () => Scaffold.of(context).openDrawer(),
                      ),
                    ))
            : IconButton(
                tooltip: strings.back,
                icon: const Icon(Icons.arrow_back),
                onPressed: () => context.go(parentRoute),
              ),
        titleSpacing: isDesktop ? 24 : 0,
        title: Row(
          children: [
            Image.asset(
              'assets/images/Rigaud_Tech_profile_transparent.png',
              width: 32,
              height: 32,
              fit: BoxFit.contain,
              errorBuilder: (context, error, stackTrace) =>
                  const Icon(Icons.hub_outlined),
            ),
            const SizedBox(width: 12),
            Flexible(
              child: Text(
                strings.appName,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ),
            if (isDesktop)
              Expanded(
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 580),
                    child: TextField(
                      decoration: InputDecoration(
                        hintText: strings.searchSystem,
                        prefixIcon: const Icon(Icons.search_outlined),
                        contentPadding: const EdgeInsets.symmetric(
                          vertical: 10,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: strings.notifications,
            onPressed: () {},
            icon: const Badge(
              smallSize: 8,
              child: Icon(Icons.notifications_none_outlined),
            ),
          ),
          IconButton(
            tooltip: strings.help,
            onPressed: () {},
            icon: const Icon(Icons.help_outline),
          ),
          if (isDesktop)
            InkWell(
              onTap: () => context.go(AppRoutes.currentUser),
              borderRadius: BorderRadius.circular(24),
              child: Padding(
                padding: const EdgeInsets.only(left: 8, right: 20),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 18,
                      backgroundColor: AppColors.brand,
                      foregroundColor: Colors.white,
                      child: Text(_initials(profileName)),
                    ),
                    const SizedBox(width: 10),
                    ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 116),
                      child: Text(
                        profileName,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ),
                    const Icon(Icons.keyboard_arrow_down_outlined),
                  ],
                ),
              ),
            ),
          ...?actions,
        ],
      ),
      drawer: isDesktop ? null : const Drawer(child: _NavigationItems()),
      body: Row(
        children: [
          if (isDesktop)
            const SizedBox(
              width: 242,
              child: Material(color: Colors.white, child: _NavigationItems()),
            ),
          Expanded(child: SafeArea(top: false, child: body)),
        ],
      ),
    );
  }
}

class _NavigationItems extends ConsumerWidget {
  const _NavigationItems();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentPath = GoRouterState.of(context).uri.path;
    final strings = ref.watch(appStringsProvider);
    final restaurantOpen = currentPath.startsWith('/restaurant');

    return DecoratedBox(
      decoration: const BoxDecoration(
        border: Border(right: BorderSide(color: Color(0xFFE7ECF4))),
      ),
      child: ListView(
        padding: const EdgeInsets.symmetric(vertical: 14),
        children: [
          _NavigationTile(
            route: AppRoutes.dashboard,
            label: strings.home,
            icon: Icons.home_outlined,
            currentPath: currentPath,
          ),
          _NavigationTile(
            route: AppRoutes.products,
            label: strings.sales,
            icon: Icons.shopping_cart_outlined,
            currentPath: currentPath,
          ),
          _RestaurantNavigation(
            currentPath: currentPath,
            expanded: restaurantOpen,
            strings: strings,
          ),
          const SizedBox(height: 10),
          _NavigationTile(
            route: AppRoutes.inventory,
            label: strings.inventory,
            icon: Icons.inventory_2_outlined,
            currentPath: currentPath,
          ),
          _NavigationTile(
            label: strings.finance,
            icon: Icons.account_balance_wallet_outlined,
            currentPath: currentPath,
          ),
          _NavigationTile(
            label: strings.reports,
            icon: Icons.bar_chart_outlined,
            currentPath: currentPath,
          ),
          _NavigationTile(
            route: AppRoutes.currentUser,
            label: strings.settings,
            icon: Icons.settings_outlined,
            currentPath: currentPath,
          ),
        ],
      ),
    );
  }
}

class _RestaurantNavigation extends StatelessWidget {
  const _RestaurantNavigation({
    required this.currentPath,
    required this.expanded,
    required this.strings,
  });

  final String currentPath;
  final bool expanded;
  final AppStrings strings;

  @override
  Widget build(BuildContext context) {
    final selected = currentPath.startsWith('/restaurant');
    return Column(
      children: [
        _NavigationTile(
          route: AppRoutes.restaurantTables,
          label: strings.restaurant,
          icon: Icons.restaurant_outlined,
          currentPath: currentPath,
          selected: selected,
          trailing: Icon(
            expanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
            color: selected ? AppColors.brand : null,
          ),
        ),
        if (expanded)
          Padding(
            padding: const EdgeInsets.only(left: 38, top: 4, bottom: 8),
            child: Column(
              children: [
                _SubNavigationTile(
                  label: strings.restaurantOverview,
                  currentPath: currentPath,
                ),
                _SubNavigationTile(
                  route: AppRoutes.restaurantTables,
                  label: strings.tables,
                  currentPath: currentPath,
                ),
                _SubNavigationTile(
                  route: AppRoutes.restaurantSectors,
                  label: strings.sectorsEnvironments,
                  currentPath: currentPath,
                ),
                _SubNavigationTile(
                  route: AppRoutes.restaurantStaff,
                  label: strings.staffTeam,
                  currentPath: currentPath,
                ),
                _SubNavigationTile(
                  route: AppRoutes.restaurantMenuAvailability,
                  label: strings.dailyMenu,
                  currentPath: currentPath,
                ),
                _SubNavigationTile(
                  label: strings.orders,
                  currentPath: currentPath,
                ),
                _SubNavigationTile(
                  label: strings.delivery,
                  currentPath: currentPath,
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _NavigationTile extends StatelessWidget {
  const _NavigationTile({
    this.route,
    required this.label,
    required this.icon,
    required this.currentPath,
    this.selected,
    this.trailing,
  });

  final String? route;
  final String label;
  final IconData icon;
  final String currentPath;
  final bool? selected;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final isSelected = selected ?? (route != null && currentPath == route);
    final isEnabled = route != null;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2, horizontal: 8),
      child: Material(
        color: isSelected ? const Color(0xFFEAF2FF) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
        child: InkWell(
          borderRadius: BorderRadius.circular(8),
          onTap: isEnabled ? () => _go(context, route!) : null,
          child: Container(
            height: 48,
            decoration: BoxDecoration(
              border: isSelected
                  ? const Border(
                      left: BorderSide(color: AppColors.brand, width: 4),
                    )
                  : null,
            ),
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: [
                Icon(
                  icon,
                  color: isEnabled
                      ? (isSelected ? AppColors.brand : const Color(0xFF53627A))
                      : const Color(0xFF98A2B3),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Text(
                    label,
                    style: TextStyle(
                      color: isEnabled
                          ? (isSelected
                                ? AppColors.brand
                                : const Color(0xFF3D4B63))
                          : const Color(0xFF98A2B3),
                      fontWeight: isSelected
                          ? FontWeight.w700
                          : FontWeight.w600,
                    ),
                  ),
                ),
                if (trailing case final Widget trailingWidget) trailingWidget,
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _SubNavigationTile extends StatelessWidget {
  const _SubNavigationTile({
    this.route,
    required this.label,
    required this.currentPath,
  });

  final String? route;
  final String label;
  final String currentPath;

  @override
  Widget build(BuildContext context) {
    final selected = route != null && route == currentPath;
    return Padding(
      padding: const EdgeInsets.only(right: 8, bottom: 2),
      child: Material(
        color: selected ? const Color(0xFFEAF2FF) : Colors.transparent,
        borderRadius: BorderRadius.circular(7),
        child: InkWell(
          borderRadius: BorderRadius.circular(7),
          onTap: route == null ? null : () => _go(context, route!),
          child: SizedBox(
            height: 40,
            child: Align(
              alignment: Alignment.centerLeft,
              child: Padding(
                padding: const EdgeInsets.only(left: 24, right: 10),
                child: Text(
                  label,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: selected ? AppColors.brand : const Color(0xFF53627A),
                    fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

void _go(BuildContext context, String route) {
  if (Scaffold.maybeOf(context)?.isDrawerOpen ?? false) {
    Navigator.of(context).pop();
  }
  context.go(route);
}

String _initials(String name) {
  final parts = name.split(' ').where((part) => part.isNotEmpty).take(2);
  final result = parts.map((part) => part[0]).join();
  return result.isEmpty ? 'RT' : result.toUpperCase();
}

String? _parentRouteFor(String path) {
  if (path == AppRoutes.companyCreate ||
      RegExp(r'^/companies/[^/]+(?:/edit)?$').hasMatch(path)) {
    return AppRoutes.companies;
  }
  if (path == AppRoutes.userCreate ||
      RegExp(r'^/users/[^/]+(?:/(?:edit|reset-password))?$').hasMatch(path)) {
    return AppRoutes.users;
  }
  if (path == AppRoutes.changeMyPassword || path == AppRoutes.mfaSettings) {
    return AppRoutes.currentUser;
  }
  if (path == AppRoutes.productCreate ||
      RegExp(r'^/products/[^/]+(?:/edit)?$').hasMatch(path)) {
    return AppRoutes.products;
  }
  if (path == AppRoutes.categoryCreate ||
      RegExp(r'^/categories/[^/]+(?:/edit)?$').hasMatch(path)) {
    return AppRoutes.categories;
  }
  if (path == AppRoutes.warehouseCreate ||
      RegExp(r'^/warehouses/[^/]+(?:/edit)?$').hasMatch(path)) {
    return AppRoutes.warehouses;
  }
  if (path == AppRoutes.warehouseZoneCreate ||
      RegExp(r'^/warehouse-zones/[^/]+(?:/edit)?$').hasMatch(path)) {
    return AppRoutes.warehouseZones;
  }
  if (path == AppRoutes.warehouseLocationCreate ||
      RegExp(r'^/warehouse-locations/[^/]+(?:/edit)?$').hasMatch(path)) {
    return AppRoutes.warehouseLocations;
  }
  if (path == AppRoutes.receivingDocumentCreate ||
      RegExp(r'^/receiving-documents/[^/]+(?:/edit)?$').hasMatch(path)) {
    return AppRoutes.receivingDocuments;
  }
  if (RegExp(r'^/audit/[^/]+$').hasMatch(path)) return AppRoutes.audit;
  return null;
}
