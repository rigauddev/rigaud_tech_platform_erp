import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/user.dart';
import 'user_controller.dart';

class UserListScreen extends ConsumerStatefulWidget {
  const UserListScreen({super.key});

  @override
  ConsumerState<UserListScreen> createState() => _UserListScreenState();
}

class _UserListScreenState extends ConsumerState<UserListScreen> {
  final _search = TextEditingController();

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final users = ref.watch(usersControllerProvider);
    return AppScaffold(
      title: 'Usuários',
      selectedIndex: 2,
      actions: [
        IconButton(
          tooltip: 'Meu perfil',
          icon: const Icon(Icons.account_circle_outlined),
          onPressed: () => context.go(AppRoutes.currentUser),
        ),
        IconButton(
          tooltip: 'Novo usuário',
          icon: const Icon(Icons.person_add_alt_outlined),
          onPressed: () => context.go(AppRoutes.userCreate),
        ),
      ],
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: TextField(
              controller: _search,
              decoration: InputDecoration(
                labelText: 'Buscar',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  tooltip: 'Aplicar busca',
                  icon: const Icon(Icons.arrow_forward),
                  onPressed: () => ref
                      .read(usersControllerProvider.notifier)
                      .reload(search: _search.text.trim()),
                ),
              ),
              onSubmitted: (value) => ref
                  .read(usersControllerProvider.notifier)
                  .reload(search: value.trim()),
            ),
          ),
          Expanded(
            child: users.when(
              data: (page) {
                if (page.items.isEmpty) {
                  return const AppEmptyState(
                    title: 'Nenhum usuário encontrado',
                    message: 'Cadastre usuários para habilitar acesso ao ERP.',
                  );
                }
                return LayoutBuilder(
                  builder: (context, constraints) {
                    if (constraints.maxWidth >= 900) {
                      return _UserTable(items: page.items);
                    }
                    return _UserCards(items: page.items);
                  },
                );
              },
              error: (error, stackTrace) =>
                  Center(child: Text(_message(error))),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ),
        ],
      ),
    );
  }

  String _message(Object error) {
    final text = error.toString();
    if (text.contains('403')) {
      return 'Acesso restrito a superusuários.';
    }
    return 'Não foi possível carregar usuários.';
  }
}

class _UserTable extends StatelessWidget {
  const _UserTable({required this.items});

  final List<UserProfile> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Nome')),
          DataColumn(label: Text('Email')),
          DataColumn(label: Text('Empresa')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Ações')),
        ],
        rows: items
            .map(
              (user) => DataRow(
                cells: [
                  DataCell(Text(user.title)),
                  DataCell(Text(user.email)),
                  DataCell(Text(user.tenantSlug)),
                  DataCell(Text(user.status.label)),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () =>
                          context.go('${AppRoutes.users}/${user.id}'),
                    ),
                  ),
                ],
              ),
            )
            .toList(),
      ),
    );
  }
}

class _UserCards extends StatelessWidget {
  const _UserCards({required this.items});

  final List<UserProfile> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final user = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.person_outline),
            title: Text(user.title),
            subtitle: Text('${user.email} · ${user.status.label}'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go('${AppRoutes.users}/${user.id}'),
          ),
        );
      },
    );
  }
}
