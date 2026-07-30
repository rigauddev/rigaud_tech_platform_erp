import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/product.dart';
import 'product_controller.dart';

class ProductDetailScreen extends ConsumerWidget {
  const ProductDetailScreen({required this.productId, super.key});

  final String productId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final product = ref.watch(productDetailsProvider(productId));
    return AppScaffold(
      title: 'Produto',
      actions: [
        IconButton(
          tooltip: 'Editar',
          icon: const Icon(Icons.edit_outlined),
          onPressed: () => context.go('${AppRoutes.products}/$productId/edit'),
        ),
      ],
      body: product.when(
        data: (item) => _ProductDetail(product: item),
        error: (error, stackTrace) =>
            Center(child: Text('Produto não encontrado.')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _ProductDetail extends ConsumerWidget {
  const _ProductDetail({required this.product});

  final Product product;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        if (product.mainImageUrl != null)
          AspectRatio(
            aspectRatio: 16 / 9,
            child: Image.network(product.mainImageUrl!, fit: BoxFit.cover),
          ),
        const SizedBox(height: AppSpacing.md),
        Text(product.name, style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: AppSpacing.sm),
        Text('${product.internalCode} · ${product.productType.label}'),
        const SizedBox(height: AppSpacing.md),
        Wrap(
          spacing: AppSpacing.md,
          runSpacing: AppSpacing.md,
          children: [
            Chip(label: Text(product.formattedSalePrice)),
            Chip(label: Text(product.unitOfMeasure.label)),
            Chip(label: Text(product.status.label)),
            Chip(
              label: Text(
                product.isAvailableForSale ? 'Disponível' : 'Indisponível',
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.md),
        if (product.description != null) Text(product.description!),
        const SizedBox(height: AppSpacing.lg),
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            AppButton(
              label: product.isActive ? 'Desativar' : 'Ativar',
              icon: product.isActive
                  ? Icons.block_outlined
                  : Icons.check_circle_outline,
              onPressed: () => product.isActive
                  ? ref
                        .read(productsControllerProvider.notifier)
                        .deactivate(product.id)
                  : ref
                        .read(productsControllerProvider.notifier)
                        .activate(product.id),
            ),
            AppButton(
              label: product.isAvailableForSale
                  ? 'Indisponibilizar'
                  : 'Disponibilizar',
              icon: Icons.sell_outlined,
              onPressed: () => ref
                  .read(productsControllerProvider.notifier)
                  .changeAvailability(product.id, !product.isAvailableForSale),
            ),
            AppButton(
              label: 'Remover',
              icon: Icons.delete_outline,
              onPressed: () async {
                await ref
                    .read(productsControllerProvider.notifier)
                    .deleteProduct(product.id);
                if (context.mounted) {
                  context.go(AppRoutes.products);
                }
              },
            ),
          ],
        ),
      ],
    );
  }
}
