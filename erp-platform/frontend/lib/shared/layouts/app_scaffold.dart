import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/router/app_routes.dart';
import '../../features/auth/presentation/auth_controller.dart';

class AppScaffold extends StatelessWidget {
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
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.sizeOf(context).width >= 1024;
    final currentPath = GoRouterState.of(context).uri.path;
    final parentRoute = _parentRouteFor(currentPath);

    return Scaffold(
      appBar: AppBar(
        title: Text(title ?? 'Rigaud Tech ERP'),
        actions: actions,
        automaticallyImplyLeading: parentRoute == null,
        leading: parentRoute == null
            ? null
            : IconButton(
                tooltip: 'Voltar',
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
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        _NavigationBrand(role: _roleLabel(user?.role, isPlatformAdmin)),
        const SizedBox(height: 12),
        _NavigationSection(
          title: 'Visão geral',
          currentPath: currentPath,
          items: const [
            _NavigationItem(
              AppRoutes.dashboard,
              'Dashboard',
              Icons.dashboard_outlined,
            ),
          ],
        ),
        _NavigationSection(
          title: 'Cadastros',
          currentPath: currentPath,
          items: [
            if (isPlatformAdmin)
              const _NavigationItem(
                AppRoutes.companies,
                'Empresas',
                Icons.business_outlined,
              ),
            if (isPlatformAdmin)
              const _NavigationItem(
                AppRoutes.users,
                'Usuários',
                Icons.people_alt_outlined,
              ),
            _NavigationItem(
              AppRoutes.products,
              'Produtos',
              Icons.inventory_2_outlined,
            ),
            _NavigationItem(
              AppRoutes.categories,
              'Categorias',
              Icons.account_tree_outlined,
            ),
          ],
        ),
        _NavigationSection(
          title: 'Estoque',
          currentPath: currentPath,
          items: const [
            _NavigationItem(
              AppRoutes.inventory,
              'Saldos e transações',
              Icons.inventory_outlined,
            ),
            _NavigationItem(
              AppRoutes.receivingDocuments,
              'Recebimentos',
              Icons.move_to_inbox_outlined,
            ),
            _NavigationItem(
              AppRoutes.warehouses,
              'Depósitos',
              Icons.warehouse_outlined,
            ),
            _NavigationItem(
              AppRoutes.warehouseZones,
              'Zonas',
              Icons.location_searching_outlined,
            ),
            _NavigationItem(
              AppRoutes.warehouseLocations,
              'Localizações',
              Icons.place_outlined,
            ),
          ],
        ),
        _NavigationSection(
          title: 'Conta e segurança',
          currentPath: currentPath,
          items: const [
            _NavigationItem(
              AppRoutes.currentUser,
              'Meu perfil',
              Icons.account_circle_outlined,
            ),
            _NavigationItem(
              AppRoutes.mfaSettings,
              'Autenticação em dois fatores',
              Icons.verified_user_outlined,
            ),
          ],
        ),
        if (isPlatformAdmin)
          _NavigationSection(
            title: 'Administração',
            currentPath: currentPath,
            items: const [
              _NavigationItem(
                AppRoutes.audit,
                'Auditoria',
                Icons.fact_check_outlined,
              ),
            ],
          ),
        if (_environment != 'production' && isPlatformAdmin)
          _NavigationSection(
            title: 'Desenvolvimento',
            currentPath: currentPath,
            items: const [
              _NavigationItem(
                AppRoutes.demo,
                'Ambiente demo',
                Icons.science_outlined,
              ),
            ],
          ),
      ],
    );
  }
}

class _NavigationBrand extends StatelessWidget {
  const _NavigationBrand({required this.role});

  final String role;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Rigaud Tech\nPlatform ERP',
            style: TextStyle(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 4),
          Text(role, style: Theme.of(context).textTheme.labelSmall),
        ],
      ),
    );
  }
}

String _roleLabel(String? role, bool isPlatformAdmin) {
  if (isPlatformAdmin) {
    return 'Administrador da plataforma';
  }
  return switch (role) {
    'company_admin' => 'Administrador da empresa',
    'branch_manager' => 'Gerente da filial',
    'branch_operator' => 'Operador da filial',
    _ => 'Usuário autenticado',
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
  if (RegExp(r'^/audit/[^/]+$').hasMatch(path)) {
    return AppRoutes.audit;
  }
  return null;
}
