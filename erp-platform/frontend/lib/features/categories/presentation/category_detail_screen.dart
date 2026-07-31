import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/category.dart';
import 'category_controller.dart';

class CategoryDetailScreen extends ConsumerWidget {
  const CategoryDetailScreen({required this.categoryId, super.key});

  final String categoryId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final category = ref.watch(categoryDetailsProvider(categoryId));
    return AppScaffold(
      title: 'Categoria',
      actions: [
        IconButton(
          tooltip: 'Editar categoria',
          icon: const Icon(Icons.edit_outlined),
          onPressed: () =>
              context.go('${AppRoutes.categories}/$categoryId/edit'),
        ),
      ],
      body: category.when(
        data: (item) => _CategoryDetail(item: item),
        error: (error, stackTrace) => Center(child: Text(error.toString())),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _CategoryDetail extends ConsumerWidget {
  const _CategoryDetail({required this.item});

  final Category item;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Text(item.name, style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: AppSpacing.sm),
        Text(item.description ?? 'Sem descrição'),
        const SizedBox(height: AppSpacing.lg),
        Wrap(
          spacing: AppSpacing.md,
          runSpacing: AppSpacing.md,
          children: [
            _Info(label: 'Código', value: item.internalCode),
            _Info(label: 'Slug', value: item.slug),
            _Info(label: 'Status', value: item.status.label),
            _Info(label: 'Ordem', value: item.displayOrder.toString()),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        Wrap(
          spacing: AppSpacing.sm,
          children: [
            FilledButton.icon(
              icon: Icon(item.isActive ? Icons.block : Icons.check_circle),
              label: Text(item.isActive ? 'Desativar' : 'Ativar'),
              onPressed: () => item.isActive
                  ? ref
                        .read(categoriesControllerProvider.notifier)
                        .deactivate(item.id)
                  : ref
                        .read(categoriesControllerProvider.notifier)
                        .activate(item.id),
            ),
            OutlinedButton.icon(
              icon: const Icon(Icons.delete_outline),
              label: const Text('Remover'),
              onPressed: () async {
                await ref
                    .read(categoriesControllerProvider.notifier)
                    .deleteCategory(item.id);
                if (context.mounted) {
                  context.go(AppRoutes.categories);
                }
              },
            ),
          ],
        ),
      ],
    );
  }
}

class _Info extends StatelessWidget {
  const _Info({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      child: ListTile(
        contentPadding: EdgeInsets.zero,
        title: Text(label),
        subtitle: Text(value),
      ),
    );
  }
}
