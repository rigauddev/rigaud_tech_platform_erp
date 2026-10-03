import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/router/app_routes.dart';
import '../../core/localization/app_strings.dart';
import '../../features/auth/presentation/auth_controller.dart';

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

    return Scaffold(
      appBar: AppBar(
        title: Text(title ?? strings.appName),
        actions: actions,
        automaticallyImplyLeading: parentRoute == null,
        leading: parentRoute == null
            ? null
            : IconButton(
                tooltip: strings.back,
                icon: const Icon(Icons.arrow_back),
                onPressed: () => context.go(parentRoute),
              ),
      ),
      drawer: isDesktop ? null : const Drawer(child: _NavigationItems()),
      body: Row(
        children: [
          if (isDesktop)
            const SizedBox(
              width: 248,
              child: Material(
                elevation: 1,
                child: SafeArea(child: _NavigationItems()),
              ),
            ),
          Expanded(child: SafeArea(child: body)),
        ],
      ),
    );
  }
}

class _NavigationItems extends ConsumerWidget {
  const _NavigationItems();

  static const _environment = String.fromEnvironment(
    'APP_ENV',
    defaultValue: 'development',
  );

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentPath = GoRouterState.of(context).uri.path;
    final user = ref.watch(authControllerProvider).value?.user;
    final isPlatformAdmin = user?.isSuperuser ?? false;
    final strings = ref.watch(appStringsProvider);
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        _NavigationBrand(
          role: _roleLabel(user?.role, isPlatformAdmin, strings),
          appName: strings.appName,
        ),
        const SizedBox(height: 12),
        _NavigationSection(
          title: strings.overview,
          currentPath: currentPath,
          items: [
            _NavigationItem(
              AppRoutes.dashboard,
              strings.dashboard,
              Icons.dashboard_outlined,
            ),
          ],
        ),
        _NavigationSection(
          title: strings.records,
          currentPath: currentPath,
          items: [
            if (isPlatformAdmin)
              _NavigationItem(
                AppRoutes.companies,
                strings.companies,
                Icons.business_outlined,
              ),
            if (isPlatformAdmin)
              _NavigationItem(
                AppRoutes.users,
                strings.users,
                Icons.people_alt_outlined,
              ),
            _NavigationItem(
              AppRoutes.products,
              strings.products,
              Icons.inventory_2_outlined,
            ),
            _NavigationItem(
              AppRoutes.categories,
              strings.categories,
              Icons.account_tree_outlined,
            ),
          ],
        ),
        _NavigationSection(
          title: strings.inventory,
          currentPath: currentPath,
          items: [
            _NavigationItem(
              AppRoutes.inventory,
              strings.balancesTransactions,
              Icons.inventory_outlined,
            ),
            _NavigationItem(
              AppRoutes.receivingDocuments,
              strings.receiving,
              Icons.move_to_inbox_outlined,
            ),
            _NavigationItem(
              AppRoutes.warehouses,
              strings.warehouses,
              Icons.warehouse_outlined,
            ),
            _NavigationItem(
              AppRoutes.warehouseZones,
              strings.zones,
              Icons.location_searching_outlined,
            ),
            _NavigationItem(
              AppRoutes.warehouseLocations,
              strings.locations,
              Icons.place_outlined,
            ),
          ],
        ),
        _NavigationSection(
          title: 'Restaurante',
          currentPath: currentPath,
          items: const [
            _NavigationItem(
              AppRoutes.restaurantTables,
              'Mesas e mapa do salão',
              Icons.table_restaurant_outlined,
            ),
          ],
        ),
        _NavigationSection(
          title: strings.accountSecurity,
          currentPath: currentPath,
          items: [
            _NavigationItem(
              AppRoutes.currentUser,
              strings.myProfile,
              Icons.account_circle_outlined,
            ),
            _NavigationItem(
              AppRoutes.mfaSettings,
              strings.mfa,
              Icons.verified_user_outlined,
            ),
          ],
        ),
        if (isPlatformAdmin)
          _NavigationSection(
            title: strings.administration,
            currentPath: currentPath,
            items: [
              _NavigationItem(
                AppRoutes.audit,
                strings.audit,
                Icons.fact_check_outlined,
              ),
            ],
          ),
        if (_environment != 'production' && isPlatformAdmin)
          _NavigationSection(
            title: strings.development,
            currentPath: currentPath,
            items: [
              _NavigationItem(
                AppRoutes.demo,
                strings.demoEnvironment,
                Icons.science_outlined,
              ),
            ],
          ),
      ],
    );
  }
}

class _NavigationBrand extends StatelessWidget {
  const _NavigationBrand({required this.role, required this.appName});

  final String role;
  final String appName;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(appName, style: TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 4),
          Text(role, style: Theme.of(context).textTheme.labelSmall),
        ],
      ),
    );
  }
}

String _roleLabel(String? role, bool isPlatformAdmin, AppStrings strings) {
  if (isPlatformAdmin) {
    return strings.platformAdministrator;
  }
  return switch (role) {
    'company_admin' => strings.companyAdministrator,
    'branch_manager' => strings.branchManager,
    'branch_operator' => strings.branchOperator,
    _ => strings.authenticatedUser,
  };
}

class _NavigationSection extends StatelessWidget {
  const _NavigationSection({
    required this.title,
    required this.currentPath,
    required this.items,
  });

  final String title;
  final String currentPath;
  final List<_NavigationItem> items;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Text(title, style: Theme.of(context).textTheme.labelMedium),
          ),
          for (final item in items)
            ListTile(
              leading: Icon(item.icon),
              title: Text(item.label),
              selected:
                  currentPath == item.route ||
                  currentPath.startsWith('${item.route}/'),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              onTap: () {
                if (Scaffold.maybeOf(context)?.isDrawerOpen ?? false) {
                  Navigator.of(context).pop();
                }
                context.go(item.route);
              },
            ),
        ],
      ),
    );
  }
}

class _NavigationItem {
  const _NavigationItem(this.route, this.label, this.icon);

  final String route;
  final String label;
  final IconData icon;
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
  if (path == AppRoutes.restaurantTables) {
    return AppRoutes.dashboard;
  }
  if (RegExp(r'^/audit/[^/]+$').hasMatch(path)) {
    return AppRoutes.audit;
  }
  return null;
}
