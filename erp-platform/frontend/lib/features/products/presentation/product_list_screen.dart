import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/product.dart';
import 'product_controller.dart';

class ProductListScreen extends ConsumerStatefulWidget {
  const ProductListScreen({super.key});

  @override
  ConsumerState<ProductListScreen> createState() => _ProductListScreenState();
}

class _ProductListScreenState extends ConsumerState<ProductListScreen> {
  final _search = TextEditingController();

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final products = ref.watch(productsControllerProvider);
    return AppScaffold(
      title: 'Produtos',
      actions: [
        IconButton(
          tooltip: 'Novo produto',
          icon: const Icon(Icons.add_box_outlined),
          onPressed: () => context.go(AppRoutes.productCreate),
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
                      .read(productsControllerProvider.notifier)
                      .reload(search: _search.text),
                ),
              ),
              onSubmitted: (value) => ref
                  .read(productsControllerProvider.notifier)
                  .reload(search: value),
            ),
          ),
          Expanded(
            child: products.when(
              data: (items) {
                if (items.isEmpty) {
                  return const AppEmptyState(
                    title: 'Nenhum produto cadastrado',
                    message:
                        'Cadastre produtos antes de avançar para categorias e estoque.',
                  );
                }
                return LayoutBuilder(
                  builder: (context, constraints) {
                    if (constraints.maxWidth >= 900) {
                      return _ProductTable(items: items);
                    }
                    return _ProductCards(items: items);
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
    return 'Não foi possível carregar produtos.';
  }
}

class _ProductTable extends StatelessWidget {
  const _ProductTable({required this.items});

  final List<Product> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Nome')),
          DataColumn(label: Text('Código')),
          DataColumn(label: Text('Tipo')),
          DataColumn(label: Text('Preço')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Ações')),
        ],
        rows: items
            .map(
              (product) => DataRow(
                cells: [
                  DataCell(Text(product.name)),
                  DataCell(Text(product.internalCode)),
                  DataCell(Text(product.productType.label)),
                  DataCell(Text(product.formattedSalePrice)),
                  DataCell(Text(_status(product))),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () =>
                          context.go('${AppRoutes.products}/${product.id}'),
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

class _ProductCards extends StatelessWidget {
  const _ProductCards({required this.items});

  final List<Product> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final product = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.inventory_2_outlined),
            title: Text(product.name),
            subtitle: Text(
              '${product.internalCode} · ${product.formattedSalePrice}',
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go('${AppRoutes.products}/${product.id}'),
          ),
        );
      },
    );
  }
}

String _status(Product product) {
  if (!product.isActive) {
    return 'Inativo';
  }
  return product.isAvailableForSale ? 'Disponível' : 'Indisponível';
}
