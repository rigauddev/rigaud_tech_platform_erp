import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/user.dart';
import 'user_controller.dart';

class UserDetailScreen extends ConsumerWidget {
  const UserDetailScreen({required this.userId, super.key});

  final String userId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(userDetailsProvider(userId));
    return AppScaffold(
      title: 'Usuário',
      selectedIndex: 2,
      body: user.when(
        data: (item) => _UserDetail(user: item),
        error: (error, stackTrace) =>
            const Center(child: Text('Usuário não encontrado.')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class CurrentUserProfileScreen extends ConsumerWidget {
  const CurrentUserProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProfileProvider);
    return AppScaffold(
      title: 'Meu perfil',
      selectedIndex: 2,
      actions: [
        IconButton(
          tooltip: 'Alterar senha',
          icon: const Icon(Icons.password_outlined),
          onPressed: () => context.go(AppRoutes.changeMyPassword),
        ),
      ],
      body: user.when(
        data: (item) => _UserDetail(user: item, readOnly: true),
        error: (error, stackTrace) =>
            const Center(child: Text('Perfil não encontrado.')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _UserDetail extends ConsumerWidget {
  const _UserDetail({required this.user, this.readOnly = false});

  final UserProfile user;
  final bool readOnly;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            Chip(label: Text(user.status.label)),
            if (user.isSuperuser) const Chip(label: Text('Superusuário')),
            if (user.mustChangePassword)
              const Chip(label: Text('Troca de senha pendente')),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        _row('Nome', user.title),
        _row('Email', user.email),
        _row('Empresa', user.tenantSlug),
        _row('Telefone', user.phone ?? '-'),
        _row('Último login', user.lastLoginAt?.toLocal().toString() ?? '-'),
        if (!readOnly) ...[
          const SizedBox(height: AppSpacing.lg),
          Wrap(
            spacing: AppSpacing.sm,
            runSpacing: AppSpacing.sm,
            children: [
              FilledButton.icon(
                icon: const Icon(Icons.edit_outlined),
                label: const Text('Editar'),
                onPressed: () =>
                    context.go('${AppRoutes.users}/${user.id}/edit'),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.check_circle_outline),
                label: const Text('Ativar'),
                onPressed: () => ref
                    .read(usersControllerProvider.notifier)
                    .activate(user.id),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.pause_circle_outline),
                label: const Text('Desativar'),
                onPressed: () => ref
                    .read(usersControllerProvider.notifier)
                    .deactivate(user.id),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.block_outlined),
                label: const Text('Bloquear'),
                onPressed: () =>
                    ref.read(usersControllerProvider.notifier).block(user.id),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.lock_open_outlined),
                label: const Text('Desbloquear'),
                onPressed: () =>
                    ref.read(usersControllerProvider.notifier).unblock(user.id),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.key_outlined),
                label: const Text('Resetar senha'),
                onPressed: () =>
                    context.go('${AppRoutes.users}/${user.id}/reset-password'),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 4),
          Text(value),
        ],
      ),
    );
  }
}
