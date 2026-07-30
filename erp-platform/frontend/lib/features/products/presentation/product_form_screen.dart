import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/product.dart';
import '../domain/product_input.dart';
import 'product_controller.dart';

class ProductFormScreen extends ConsumerStatefulWidget {
  const ProductFormScreen({this.productId, super.key});

  final String? productId;

  @override
  ConsumerState<ProductFormScreen> createState() => _ProductFormScreenState();
}

class _ProductFormScreenState extends ConsumerState<ProductFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _internalCode = TextEditingController();
  final _description = TextEditingController();
  final _barcode = TextEditingController();
  final _salePrice = TextEditingController(text: '0.00');
  final _costPrice = TextEditingController(text: '0.00');
  final _mainImageUrl = TextEditingController();
  ProductType _productType = ProductType.simple;
  UnitOfMeasure _unit = UnitOfMeasure.unit;
  bool _available = true;
  bool _hydrated = false;
  bool _saving = false;

  bool get _isEditing => widget.productId != null;

  @override
  void dispose() {
    _name.dispose();
    _internalCode.dispose();
    _description.dispose();
    _barcode.dispose();
    _salePrice.dispose();
    _costPrice.dispose();
    _mainImageUrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final details = _isEditing
        ? ref.watch(productDetailsProvider(widget.productId!))
        : null;
    details?.whenData(_hydrate);

    return AppScaffold(
      title: _isEditing ? 'Editar produto' : 'Novo produto',
      body:
          details?.when(
            data: (_) => _buildForm(context),
            error: (error, stackTrace) => Center(child: Text(_message(error))),
            loading: () => const Center(child: CircularProgressIndicator()),
          ) ??
          _buildForm(context),
    );
  }

  void _hydrate(Product product) {
    if (_hydrated) {
      return;
    }
    _name.text = product.name;
    _internalCode.text = product.internalCode;
    _description.text = product.description ?? '';
    _barcode.text = product.barcode ?? '';
    _salePrice.text = product.salePrice;
    _costPrice.text = product.costPrice;
    _mainImageUrl.text = product.mainImageUrl ?? '';
    _productType = product.productType;
    _unit = product.unitOfMeasure;
    _available = product.isAvailableForSale;
    _hydrated = true;
  }

  Widget _buildForm(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Form(
        key: _formKey,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth >= 800;
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Wrap(
                  spacing: AppSpacing.md,
                  runSpacing: AppSpacing.md,
                  children: [
                    _sized(_field(_name, 'Nome'), constraints, isWide),
                    _sized(
                      _field(_internalCode, 'Código interno'),
                      constraints,
                      isWide,
                    ),
                    _sized(
                      _field(_barcode, 'Código de barras', required: false),
                      constraints,
                      isWide,
                    ),
                    _sized(
                      _field(_salePrice, 'Preço de venda', validator: _money),
                      constraints,
                      isWide,
                    ),
                    _sized(
                      _field(_costPrice, 'Custo', validator: _money),
                      constraints,
                      isWide,
                    ),
                    _sized(_typeField(), constraints, isWide),
                    _sized(_unitField(), constraints, isWide),
                    _sized(
                      _field(
                        _mainImageUrl,
                        'Imagem principal',
                        required: false,
                      ),
                      constraints,
                      isWide,
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(
                  controller: _description,
                  minLines: 3,
                  maxLines: 5,
                  decoration: const InputDecoration(labelText: 'Descrição'),
                ),
                const SizedBox(height: AppSpacing.md),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Disponível para venda'),
                  value: _available,
                  onChanged: (value) => setState(() => _available = value),
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
            );
          },
        ),
      ),
    );
  }

  SizedBox _sized(Widget child, BoxConstraints constraints, bool isWide) {
    return SizedBox(
      width: isWide
          ? (constraints.maxWidth - AppSpacing.md) / 2
          : double.infinity,
      child: child,
    );
  }

  TextFormField _field(
    TextEditingController controller,
    String label, {
    bool required = true,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
      validator: validator ?? (required ? _required : null),
    );
  }

  DropdownButtonFormField<ProductType> _typeField() {
    return DropdownButtonFormField<ProductType>(
      initialValue: _productType,
      decoration: const InputDecoration(labelText: 'Tipo'),
      items: ProductType.values
          .map((type) => DropdownMenuItem(value: type, child: Text(type.label)))
          .toList(),
      onChanged: (value) =>
          setState(() => _productType = value ?? ProductType.simple),
    );
  }

  DropdownButtonFormField<UnitOfMeasure> _unitField() {
    return DropdownButtonFormField<UnitOfMeasure>(
      initialValue: _unit,
      decoration: const InputDecoration(labelText: 'Unidade'),
      items: UnitOfMeasure.values
          .map((unit) => DropdownMenuItem(value: unit, child: Text(unit.label)))
          .toList(),
      onChanged: (value) => setState(() => _unit = value ?? UnitOfMeasure.unit),
    );
  }

  String? _required(String? value) {
    return value == null || value.trim().isEmpty ? 'Campo obrigatório' : null;
  }

  String? _money(String? value) {
    final parsed = double.tryParse((value ?? '').replaceAll(',', '.'));
    if (parsed == null || parsed < 0) {
      return 'Valor inválido';
    }
    return null;
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    setState(() => _saving = true);
    final input = ProductInput(
      name: _name.text.trim(),
      internalCode: _internalCode.text.trim().toUpperCase(),
      description: _emptyAsNull(_description.text),
      barcode: _emptyAsNull(_barcode.text),
      productType: _productType,
      unitOfMeasure: _unit,
      salePrice: _salePrice.text.trim().replaceAll(',', '.'),
      costPrice: _costPrice.text.trim().replaceAll(',', '.'),
      mainImageUrl: _emptyAsNull(_mainImageUrl.text),
      isAvailableForSale: _available,
    );
    final controller = ref.read(productsControllerProvider.notifier);
    final product = _isEditing
        ? await controller.updateProduct(widget.productId!, input)
        : await controller.create(input);
    if (!mounted) {
      return;
    }
    setState(() => _saving = false);
    if (product != null) {
      context.go('${AppRoutes.products}/${product.id}');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_message(ref.read(productsControllerProvider).error)),
        ),
      );
    }
  }

  String? _emptyAsNull(String value) {
    final text = value.trim();
    return text.isEmpty ? null : text;
  }

  String _message(Object? error) {
    final message = error?.toString() ?? 'Não foi possível salvar o produto.';
    if (message.contains('409')) {
      return 'Código interno ou código de barras já cadastrado.';
    }
    if (message.contains('404')) {
      return 'Produto não encontrado.';
    }
    return 'Não foi possível salvar o produto.';
  }
}
