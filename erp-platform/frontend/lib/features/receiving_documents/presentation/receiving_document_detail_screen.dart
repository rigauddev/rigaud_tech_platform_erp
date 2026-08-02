import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/receiving_document.dart';
import 'receiving_document_controller.dart';

class ReceivingDocumentDetailScreen extends ConsumerWidget {
  const ReceivingDocumentDetailScreen({required this.documentId, super.key});

  final String documentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final document = ref.watch(receivingDocumentDetailsProvider(documentId));
    return AppScaffold(
      title: 'Recebimento',
      actions: [
        IconButton(
          tooltip: 'Editar recebimento',
          icon: const Icon(Icons.edit_outlined),
          onPressed: () =>
              context.go('${AppRoutes.receivingDocuments}/$documentId/edit'),
        ),
      ],
      body: document.when(
        data: (item) => _Detail(document: item),
        error: (error, stackTrace) => Center(child: Text(error.toString())),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _Detail extends ConsumerWidget {
  const _Detail({required this.document});

  final ReceivingDocument document;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Wrap(
          spacing: AppSpacing.md,
          runSpacing: AppSpacing.md,
          children: [
            _Info(label: 'Documento', value: document.documentNumber),
            _Info(label: 'Tipo', value: document.documentType),
            _Info(label: 'Status', value: document.status.label),
            _Info(
              label: 'Qtd. pedida',
              value: document.orderedTotal.toStringAsFixed(3),
            ),
            _Info(
              label: 'Qtd. pendente',
              value: document.pendingTotal.toStringAsFixed(3),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: ReceivingDocumentStatus.values
              .map(
                (status) => OutlinedButton(
                  onPressed: status == document.status
                      ? null
                      : () => ref
                            .read(receivingDocumentsControllerProvider.notifier)
                            .changeStatus(document.id, status),
                  child: Text(status.label),
                ),
              )
              .toList(),
        ),
        const SizedBox(height: AppSpacing.lg),
        Text('Itens', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: AppSpacing.sm),
        ...document.items.map(
          (item) => Card(
            child: ListTile(
              leading: const Icon(Icons.inventory_2_outlined),
              title: Text(item.productId),
              subtitle: Text(
                'Pedido ${item.orderedQuantity.toStringAsFixed(3)} · Recebido ${item.receivedQuantity.toStringAsFixed(3)} · Avariado ${item.damagedQuantity.toStringAsFixed(3)}',
              ),
              trailing: Text(item.pendingQuantity.toStringAsFixed(3)),
            ),
          ),
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
      width: 180,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: Theme.of(context).textTheme.labelMedium),
              const SizedBox(height: AppSpacing.xs),
              Text(value, style: Theme.of(context).textTheme.titleMedium),
            ],
          ),
        ),
      ),
    );
  }
}
