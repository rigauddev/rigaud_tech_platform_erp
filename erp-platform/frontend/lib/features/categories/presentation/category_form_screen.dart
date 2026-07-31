import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/category.dart';
import '../domain/category_input.dart';
import 'category_controller.dart';

class CategoryFormScreen extends ConsumerStatefulWidget {
  const CategoryFormScreen({this.categoryId, super.key});

  final String? categoryId;

  @override
  ConsumerState<CategoryFormScreen> createState() => _CategoryFormScreenState();
}

class _CategoryFormScreenState extends ConsumerState<CategoryFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _internalCode = TextEditingController();
  final _parentId = TextEditingController();
  final _slug = TextEditingController();
  final _description = TextEditingController();
  final _icon = TextEditingController();
  final _color = TextEditingController();
  final _displayOrder = TextEditingController(text: '0');
  bool _hydrated = false;
  bool _saving = false;

  bool get _isEditing => widget.categoryId != null;

  @override
  void dispose() {
    _name.dispose();
    _internalCode.dispose();
    _parentId.dispose();
    _slug.dispose();
    _description.dispose();
    _icon.dispose();
    _color.dispose();
    _displayOrder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final details = _isEditing
        ? ref.watch(categoryDetailsProvider(widget.categoryId!))
        : null;
    details?.whenData(_hydrate);

    return AppScaffold(
      title: _isEditing ? 'Editar categoria' : 'Nova categoria',
      body:
          details?.when(
            data: (_) => _buildForm(context),
            error: (error, stackTrace) => Center(child: Text(_message(error))),
            loading: () => const Center(child: CircularProgressIndicator()),
          ) ??
          _buildForm(context),
    );
  }

  void _hydrate(Category category) {
    if (_hydrated) {
      return;
    }
    _name.text = category.name;
    _internalCode.text = category.internalCode;
    _parentId.text = category.parentId ?? '';
    _slug.text = category.slug;
    _description.text = category.description ?? '';
    _icon.text = category.icon ?? '';
    _color.text = category.color ?? '';
    _displayOrder.text = category.displayOrder.toString();
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
                      _field(_slug, 'Slug', required: false),
                      constraints,
                      isWide,
                    ),
                    _sized(
                      _field(_parentId, 'Categoria pai', required: false),
                      constraints,
                      isWide,
                    ),
                    _sized(
                      _field(_icon, 'Ícone', required: false),
                      constraints,
                      isWide,
                    ),
                    _sized(
                      _field(_color, 'Cor', required: false),
                      constraints,
                      isWide,
                    ),
                    _sized(
                      _field(
                        _displayOrder,
                        'Ordem',
                        validator: _nonNegativeInt,
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

  String? _required(String? value) {
    return value == null || value.trim().isEmpty ? 'Campo obrigatório' : null;
  }

  String? _nonNegativeInt(String? value) {
    final parsed = int.tryParse(value ?? '');
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
    final input = CategoryInput(
      name: _name.text.trim(),
      internalCode: _internalCode.text.trim().toUpperCase(),
      parentId: _emptyAsNull(_parentId.text),
      slug: _emptyAsNull(_slug.text),
      description: _emptyAsNull(_description.text),
      icon: _emptyAsNull(_icon.text),
      color: _emptyAsNull(_color.text),
      displayOrder: int.tryParse(_displayOrder.text) ?? 0,
    );
    final controller = ref.read(categoriesControllerProvider.notifier);
    final category = _isEditing
        ? await controller.updateCategory(widget.categoryId!, input)
        : await controller.create(input);
    if (!mounted) {
      return;
    }
    setState(() => _saving = false);
    if (category != null) {
      context.go('${AppRoutes.categories}/${category.id}');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_message(ref.read(categoriesControllerProvider).error)),
        ),
      );
    }
  }

  String? _emptyAsNull(String value) {
    final trimmed = value.trim();
    return trimmed.isEmpty ? null : trimmed;
  }

  String _message(Object? error) {
    final text = error.toString();
    if (text.contains('requestId')) {
      return text;
    }
    return 'Não foi possível salvar a categoria.';
  }
}
