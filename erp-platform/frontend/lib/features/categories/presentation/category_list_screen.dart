import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/category.dart';
import 'category_controller.dart';

class CategoryListScreen extends ConsumerStatefulWidget {
  const CategoryListScreen({super.key});

  @override
  ConsumerState<CategoryListScreen> createState() => _CategoryListScreenState();
}

class _CategoryListScreenState extends ConsumerState<CategoryListScreen> {
  final _search = TextEditingController();

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final categories = ref.watch(categoriesControllerProvider);
    return AppScaffold(
      title: 'Categorias',
      actions: [
        IconButton(
          tooltip: 'Nova categoria',
          icon: const Icon(Icons.create_new_folder_outlined),
          onPressed: () => context.go(AppRoutes.categoryCreate),
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
                  tooltip: 'Aplicar filtro',
                  icon: const Icon(Icons.filter_alt_outlined),
                  onPressed: () => ref
                      .read(categoriesControllerProvider.notifier)
                      .reload(search: _search.text),
                ),
              ),
              onSubmitted: (value) => ref
                  .read(categoriesControllerProvider.notifier)
                  .reload(search: value),
            ),
          ),
          Expanded(
            child: categories.when(
              data: (items) {
                if (items.isEmpty) {
                  return const AppEmptyState(
                    title: 'Nenhuma categoria cadastrada',
                    message:
                        'Crie categorias compartilhadas para produtos, cardápio e novos segmentos.',
                  );
                }
                return LayoutBuilder(
                  builder: (context, constraints) {
                    if (constraints.maxWidth >= 900) {
                      return _CategoryTreeTable(items: items);
                    }
                    return _CategoryHierarchyList(items: items);
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
    if (text.contains('requestId')) {
      return text;
    }
    return 'Não foi possível carregar categorias.';
  }
}

class _CategoryTreeTable extends StatelessWidget {
  const _CategoryTreeTable({required this.items});

  final List<Category> items;

  @override
  Widget build(BuildContext context) {
    final rows = <_CategoryRow>[];
    for (final item in items) {
      _flatten(item, rows, 0);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Nome')),
          DataColumn(label: Text('Código')),
          DataColumn(label: Text('Slug')),
          DataColumn(label: Text('Ordem')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Ações')),
        ],
        rows: rows
            .map(
              (row) => DataRow(
                cells: [
                  DataCell(
                    Padding(
                      padding: EdgeInsets.only(left: row.depth * AppSpacing.lg),
                      child: Text(row.category.name),
                    ),
                  ),
                  DataCell(Text(row.category.internalCode)),
                  DataCell(Text(row.category.slug)),
                  DataCell(Text(row.category.displayOrder.toString())),
                  DataCell(Text(row.category.status.label)),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () => context.go(
                        '${AppRoutes.categories}/${row.category.id}',
                      ),
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

class _CategoryHierarchyList extends StatelessWidget {
  const _CategoryHierarchyList({required this.items});

  final List<Category> items;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: items
          .map((category) => _CategoryTile(category: category, depth: 0))
          .toList(),
    );
  }
}

class _CategoryTile extends StatelessWidget {
  const _CategoryTile({required this.category, required this.depth});

  final Category category;
  final int depth;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(left: depth * AppSpacing.md),
      child: Column(
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.account_tree_outlined),
              title: Text(category.name),
              subtitle: Text('${category.internalCode} · ${category.slug}'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.go('${AppRoutes.categories}/${category.id}'),
            ),
          ),
          ...category.children.map(
            (child) => _CategoryTile(category: child, depth: depth + 1),
          ),
        ],
      ),
    );
  }
}

class _CategoryRow {
  const _CategoryRow(this.category, this.depth);

  final Category category;
  final int depth;
}

void _flatten(Category category, List<_CategoryRow> rows, int depth) {
  rows.add(_CategoryRow(category, depth));
  for (final child in category.children) {
    _flatten(child, rows, depth + 1);
  }
}
