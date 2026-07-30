import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/router/app_routes.dart';

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

    return Scaffold(
      appBar: AppBar(title: Text(title ?? 'Rigaud Tech ERP'), actions: actions),
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

class _NavigationItems extends StatelessWidget {
  const _NavigationItems();

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        ListTile(
          leading: const Icon(Icons.dashboard_outlined),
          title: const Text('Dashboard'),
          onTap: () => context.go(AppRoutes.dashboard),
        ),
        ListTile(
          leading: const Icon(Icons.business_outlined),
          title: const Text('Empresas'),
          onTap: () => context.go(AppRoutes.companies),
        ),
        ListTile(
          leading: const Icon(Icons.people_alt_outlined),
          title: const Text('Usuários'),
          onTap: () => context.go(AppRoutes.users),
        ),
        ListTile(
          leading: const Icon(Icons.account_circle_outlined),
          title: const Text('Meu perfil'),
          onTap: () => context.go(AppRoutes.currentUser),
        ),
        ListTile(
          leading: const Icon(Icons.verified_user_outlined),
          title: const Text('2FA'),
          onTap: () => context.go(AppRoutes.mfaSettings),
        ),
        ListTile(
          leading: const Icon(Icons.inventory_2_outlined),
          title: const Text('Produtos'),
          onTap: () => context.go(AppRoutes.products),
        ),
        ListTile(
          leading: const Icon(Icons.fact_check_outlined),
          title: const Text('Auditoria'),
          onTap: () => context.go(AppRoutes.audit),
        ),
        const ListTile(
          leading: Icon(Icons.inventory_2_outlined),
          title: Text('Operações'),
        ),
      ],
    );
  }
}
