import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/warehouse.dart';
import '../domain/warehouse_input.dart';
import 'warehouse_controller.dart';

class WarehouseFormScreen extends ConsumerStatefulWidget {
  const WarehouseFormScreen({this.warehouseId, super.key});

  final String? warehouseId;

  @override
  ConsumerState<WarehouseFormScreen> createState() =>
      _WarehouseFormScreenState();
}

class _WarehouseFormScreenState extends ConsumerState<WarehouseFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _code = TextEditingController();
  final _name = TextEditingController();
  final _description = TextEditingController();
  final _address = TextEditingController();
  bool _isDefault = false;
  bool _isActive = true;
  bool _hydrated = false;
  bool _saving = false;

  bool get _isEditing => widget.warehouseId != null;

  @override
  void dispose() {
    _code.dispose();
    _name.dispose();
    _description.dispose();
    _address.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final details = _isEditing
        ? ref.watch(warehouseDetailsProvider(widget.warehouseId!))
        : null;
    details?.whenData(_hydrate);

    return AppScaffold(
      title: _isEditing ? 'Editar depósito' : 'Novo depósito',
      body:
          details?.when(
            data: (_) => _buildForm(context),
            error: (error, stackTrace) => Center(child: Text(_message(error))),
            loading: () => const Center(child: CircularProgressIndicator()),
          ) ??
          _buildForm(context),
    );
  }

  void _hydrate(Warehouse warehouse) {
    if (_hydrated) {
      return;
    }
    _code.text = warehouse.code;
    _name.text = warehouse.name;
    _description.text = warehouse.description ?? '';
    _address.text = warehouse.address ?? '';
    _isDefault = warehouse.isDefault;
    _isActive = warehouse.isActive;
    _hydrated = true;
  }

  Widget _buildForm(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Form(
        key: _formKey,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  SizedBox(width: 260, child: _field(_code, 'Código')),
                  SizedBox(width: 460, child: _field(_name, 'Nome')),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: _description,
                minLines: 2,
                maxLines: 4,
                decoration: const InputDecoration(labelText: 'Descrição'),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: _address,
                minLines: 2,
                maxLines: 4,
                decoration: const InputDecoration(labelText: 'Endereço'),
              ),
              const SizedBox(height: AppSpacing.md),
              SwitchListTile(
                value: _isActive,
                title: const Text('Ativo'),
                onChanged: (value) => setState(() => _isActive = value),
              ),
              SwitchListTile(
                value: _isDefault,
                title: const Text('Depósito padrão da filial'),
                onChanged: (value) => setState(() => _isDefault = value),
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

  TextFormField _field(TextEditingController controller, String label) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
      validator: (value) =>
          value == null || value.trim().isEmpty ? 'Campo obrigatório' : null,
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    setState(() => _saving = true);
    final input = WarehouseInput(
      code: _code.text.trim().toUpperCase(),
      name: _name.text.trim(),
      description: _emptyAsNull(_description.text),
      address: _emptyAsNull(_address.text),
      isDefault: _isDefault,
      isActive: _isActive,
    );
    final controller = ref.read(warehousesControllerProvider.notifier);
    final warehouse = _isEditing
        ? await controller.updateWarehouse(widget.warehouseId!, input)
        : await controller.create(input);
    if (!mounted) {
      return;
    }
    setState(() => _saving = false);
    if (warehouse != null) {
      context.go('${AppRoutes.warehouses}/${warehouse.id}');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_message(ref.read(warehousesControllerProvider).error)),
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
    return 'Não foi possível salvar o depósito.';
  }
}
