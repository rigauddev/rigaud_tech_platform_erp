import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../../products/domain/product.dart';
import '../../products/presentation/product_controller.dart';
import '../../warehouses/domain/warehouse.dart';
import '../../warehouses/presentation/warehouse_controller.dart';
import '../domain/receiving_document.dart';
import '../domain/receiving_document_input.dart';
import 'receiving_document_controller.dart';

class ReceivingDocumentFormScreen extends ConsumerStatefulWidget {
  const ReceivingDocumentFormScreen({this.documentId, super.key});

  final String? documentId;

  @override
  ConsumerState<ReceivingDocumentFormScreen> createState() =>
      _ReceivingDocumentFormScreenState();
}

class _ReceivingDocumentFormScreenState
    extends ConsumerState<ReceivingDocumentFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _documentNumber = TextEditingController();
  final _documentType = TextEditingController(text: 'invoice');
  final _notes = TextEditingController();
  String? _warehouseId;
  ReceivingDocumentStatus _status = ReceivingDocumentStatus.draft;
  final List<_ItemControllers> _items = [_ItemControllers()];
  bool _hydrated = false;
  bool _saving = false;

  bool get _isEditing => widget.documentId != null;

  @override
  void dispose() {
    _documentNumber.dispose();
    _documentType.dispose();
    _notes.dispose();
    for (final item in _items) {
      item.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final details = _isEditing
        ? ref.watch(receivingDocumentDetailsProvider(widget.documentId!))
        : null;
    details?.whenData(_hydrate);
    final warehouses = ref.watch(warehousesControllerProvider);
    final products = ref.watch(productsControllerProvider);
    return AppScaffold(
      title: _isEditing ? 'Editar recebimento' : 'Novo recebimento',
      body: warehouses.when(
        data: (warehouseItems) => products.when(
          data: (productItems) =>
              details?.when(
                data: (_) => _buildForm(context, warehouseItems, productItems),
                error: (error, stackTrace) =>
                    Center(child: Text(error.toString())),
                loading: () => const Center(child: CircularProgressIndicator()),
              ) ??
              _buildForm(context, warehouseItems, productItems),
          error: (error, stackTrace) => Center(child: Text(error.toString())),
          loading: () => const Center(child: CircularProgressIndicator()),
        ),
        error: (error, stackTrace) => Center(child: Text(error.toString())),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  void _hydrate(ReceivingDocument document) {
    if (_hydrated) {
      return;
    }
    _warehouseId = document.warehouseId;
    _documentNumber.text = document.documentNumber;
    _documentType.text = document.documentType;
    _notes.text = document.notes ?? '';
    _status = document.status;
    for (final item in _items) {
      item.dispose();
    }
    _items
      ..clear()
      ..addAll(
        document.items.map(
          (item) => _ItemControllers(
            productId: item.productId,
            orderedQuantity: item.orderedQuantity.toString(),
            receivedQuantity: item.receivedQuantity.toString(),
            damagedQuantity: item.damagedQuantity.toString(),
            unitCost: item.unitCost.toString(),
          ),
        ),
      );
    _hydrated = true;
  }

  Widget _buildForm(
    BuildContext context,
    List<Warehouse> warehouses,
    List<Product> products,
  ) {
    final activeWarehouses = warehouses
        .where((warehouse) => warehouse.isActive)
        .toList();
    final activeProducts = products
        .where((product) => product.isActive)
        .toList();
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Form(
        key: _formKey,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 980),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  SizedBox(
                    width: 300,
                    child: DropdownButtonFormField<String>(
                      initialValue: _warehouseId,
                      decoration: const InputDecoration(labelText: 'Depósito'),
                      items: activeWarehouses
                          .map(
                            (warehouse) => DropdownMenuItem(
                              value: warehouse.id,
                              child: Text(
                                '${warehouse.name} · ${warehouse.code}',
                              ),
                            ),
                          )
                          .toList(),
                      onChanged: (value) =>
                          setState(() => _warehouseId = value),
                      validator: _required,
                    ),
                  ),
                  SizedBox(
                    width: 180,
                    child: _requiredField(_documentNumber, 'Documento'),
                  ),
                  SizedBox(
                    width: 180,
                    child: _requiredField(_documentType, 'Tipo'),
                  ),
                  SizedBox(
                    width: 180,
                    child: DropdownButtonFormField<ReceivingDocumentStatus>(
                      initialValue: _status,
                      decoration: const InputDecoration(labelText: 'Status'),
                      items: ReceivingDocumentStatus.values
                          .map(
                            (status) => DropdownMenuItem(
                              value: status,
                              child: Text(status.label),
                            ),
                          )
                          .toList(),
                      onChanged: (value) =>
                          setState(() => _status = value ?? _status),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: _notes,
                maxLines: 3,
                decoration: const InputDecoration(labelText: 'Observações'),
              ),
              const SizedBox(height: AppSpacing.lg),
              Row(
                children: [
                  Text('Itens', style: Theme.of(context).textTheme.titleMedium),
                  const Spacer(),
                  IconButton(
                    tooltip: 'Adicionar item',
                    icon: const Icon(Icons.add_circle_outline),
                    onPressed: () =>
                        setState(() => _items.add(_ItemControllers())),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.sm),
              ..._items.asMap().entries.map(
                (entry) => _ItemFields(
                  item: entry.value,
                  products: activeProducts,
                  canRemove: _items.length > 1,
                  onRemove: () => setState(() {
                    final item = _items.removeAt(entry.key);
                    item.dispose();
                  }),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),
              Align(
                alignment: Alignment.centerRight,
                child: AppButton(
                  label: 'Salvar',
                  icon: Icons.save_outlined,
                  isLoading: _saving,
                  onPressed: _save,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  TextFormField _requiredField(TextEditingController controller, String label) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
      validator: _required,
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate() || _warehouseId == null) {
      return;
    }
    setState(() => _saving = true);
    final input = ReceivingDocumentInput(
      warehouseId: _warehouseId!,
      documentNumber: _documentNumber.text.trim(),
      documentType: _documentType.text.trim(),
      status: _status,
      notes: _notes.text.trim().isEmpty ? null : _notes.text.trim(),
      items: _items
          .map(
            (item) => ReceivingItemInput(
              productId: item.productId!,
              orderedQuantity: _number(item.orderedQuantity.text),
              receivedQuantity: _number(item.receivedQuantity.text),
              damagedQuantity: _number(item.damagedQuantity.text),
              unitCost: _number(item.unitCost.text),
            ),
          )
          .toList(),
    );
    final controller = ref.read(receivingDocumentsControllerProvider.notifier);
    final result = _isEditing
        ? await controller.updateDocument(widget.documentId!, input)
        : await controller.create(input);
    if (!mounted) {
      return;
    }
    setState(() => _saving = false);
    if (result != null) {
      context.go('${AppRoutes.receivingDocuments}/${result.id}');
    }
  }
}

class _ItemFields extends StatelessWidget {
  const _ItemFields({
    required this.item,
    required this.products,
    required this.canRemove,
    required this.onRemove,
  });

  final _ItemControllers item;
  final List<Product> products;
  final bool canRemove;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Wrap(
        spacing: AppSpacing.md,
        runSpacing: AppSpacing.sm,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          SizedBox(
            width: 300,
            child: DropdownButtonFormField<String>(
              initialValue: item.productId,
              decoration: const InputDecoration(labelText: 'Produto'),
              items: products
                  .map(
                    (product) => DropdownMenuItem(
                      value: product.id,
                      child: Text('${product.name} · ${product.internalCode}'),
                    ),
                  )
                  .toList(),
              onChanged: (value) => item.productId = value,
              validator: _required,
            ),
          ),
          SizedBox(
            width: 140,
            child: _decimalField(
              item.orderedQuantity,
              'Pedida',
              required: true,
            ),
          ),
          SizedBox(
            width: 140,
            child: _decimalField(item.receivedQuantity, 'Recebida'),
          ),
          SizedBox(
            width: 140,
            child: _decimalField(item.damagedQuantity, 'Avariada'),
          ),
          SizedBox(width: 140, child: _decimalField(item.unitCost, 'Custo')),
          IconButton(
            tooltip: 'Remover item',
            icon: const Icon(Icons.remove_circle_outline),
            onPressed: canRemove ? onRemove : null,
          ),
        ],
      ),
    );
  }
}

class _ItemControllers {
  _ItemControllers({
    this.productId,
    String orderedQuantity = '',
    String receivedQuantity = '0',
    String damagedQuantity = '0',
    String unitCost = '0',
  }) : orderedQuantity = TextEditingController(text: orderedQuantity),
       receivedQuantity = TextEditingController(text: receivedQuantity),
       damagedQuantity = TextEditingController(text: damagedQuantity),
       unitCost = TextEditingController(text: unitCost);

  String? productId;
  final TextEditingController orderedQuantity;
  final TextEditingController receivedQuantity;
  final TextEditingController damagedQuantity;
  final TextEditingController unitCost;

  void dispose() {
    orderedQuantity.dispose();
    receivedQuantity.dispose();
    damagedQuantity.dispose();
    unitCost.dispose();
  }
}

TextFormField _decimalField(
  TextEditingController controller,
  String label, {
  bool required = false,
}) {
  return TextFormField(
    controller: controller,
    keyboardType: TextInputType.number,
    decoration: InputDecoration(labelText: label),
    validator: (value) {
      if ((value == null || value.trim().isEmpty) && !required) {
        return null;
      }
      final number = double.tryParse((value ?? '').replaceAll(',', '.'));
      return number == null || number < 0 ? 'Valor inválido' : null;
    },
  );
}

String? _required(Object? value) {
  if (value == null) {
    return 'Obrigatório';
  }
  if (value is String && value.trim().isEmpty) {
    return 'Obrigatório';
  }
  return null;
}

double _number(String value) {
  return double.tryParse(value.replaceAll(',', '.')) ?? 0;
}
