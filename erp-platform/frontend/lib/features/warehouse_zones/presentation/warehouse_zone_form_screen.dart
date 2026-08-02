import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../../warehouses/domain/warehouse.dart';
import '../../warehouses/presentation/warehouse_controller.dart';
import '../domain/warehouse_zone.dart';
import '../domain/warehouse_zone_input.dart';
import 'warehouse_zone_controller.dart';

class WarehouseZoneFormScreen extends ConsumerStatefulWidget {
  const WarehouseZoneFormScreen({this.zoneId, super.key});

  final String? zoneId;

  @override
  ConsumerState<WarehouseZoneFormScreen> createState() =>
      _WarehouseZoneFormScreenState();
}

class _WarehouseZoneFormScreenState
    extends ConsumerState<WarehouseZoneFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _code = TextEditingController();
  final _name = TextEditingController();
  final _description = TextEditingController();
  final _color = TextEditingController();
  final _icon = TextEditingController();
  final _sortOrder = TextEditingController(text: '0');
  String? _warehouseId;
  WarehouseZoneType _type = WarehouseZoneType.storage;
  bool _isReceiving = false;
  bool _isShipping = false;
  bool _isStorage = true;
  bool _isProduction = false;
  bool _isQuarantine = false;
  bool _isActive = true;
  bool _hydrated = false;
  bool _saving = false;

  bool get _isEditing => widget.zoneId != null;

  @override
  void dispose() {
    _code.dispose();
    _name.dispose();
    _description.dispose();
    _color.dispose();
    _icon.dispose();
    _sortOrder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final details = _isEditing
        ? ref.watch(warehouseZoneDetailsProvider(widget.zoneId!))
        : null;
    details?.whenData(_hydrate);
    final warehouses = ref.watch(warehousesControllerProvider);

    return AppScaffold(
      title: _isEditing ? 'Editar zona' : 'Nova zona',
      body: warehouses.when(
        data: (items) =>
            details?.when(
              data: (_) => _buildForm(context, items),
              error: (error, stackTrace) =>
                  Center(child: Text(_message(error))),
              loading: () => const Center(child: CircularProgressIndicator()),
            ) ??
            _buildForm(context, items),
        error: (error, stackTrace) => Center(child: Text(_message(error))),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  void _hydrate(WarehouseZone zone) {
    if (_hydrated) {
      return;
    }
    _warehouseId = zone.warehouseId;
    _code.text = zone.code;
    _name.text = zone.name;
    _description.text = zone.description ?? '';
    _color.text = zone.color ?? '';
    _icon.text = zone.icon ?? '';
    _sortOrder.text = zone.sortOrder.toString();
    _type = zone.type;
    _isReceiving = zone.isReceiving;
    _isShipping = zone.isShipping;
    _isStorage = zone.isStorage;
    _isProduction = zone.isProduction;
    _isQuarantine = zone.isQuarantine;
    _isActive = zone.isActive;
    _hydrated = true;
  }

  Widget _buildForm(BuildContext context, List<Warehouse> warehouses) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Form(
        key: _formKey,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 820),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              DropdownButtonFormField<String>(
                initialValue: _warehouseId,
                decoration: const InputDecoration(labelText: 'Depósito'),
                items: warehouses
                    .where((warehouse) => warehouse.isActive)
                    .map(
                      (warehouse) => DropdownMenuItem(
                        value: warehouse.id,
                        child: Text('${warehouse.name} · ${warehouse.code}'),
                      ),
                    )
                    .toList(),
                onChanged: (value) => setState(() => _warehouseId = value),
                validator: (value) =>
                    value == null || value.isEmpty ? 'Campo obrigatório' : null,
              ),
              const SizedBox(height: AppSpacing.md),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  SizedBox(width: 220, child: _field(_code, 'Código')),
                  SizedBox(width: 360, child: _field(_name, 'Nome')),
                  SizedBox(width: 160, child: _numberField()),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              DropdownButtonFormField<WarehouseZoneType>(
                initialValue: _type,
                decoration: const InputDecoration(labelText: 'Tipo'),
                items: WarehouseZoneType.values
                    .map(
                      (type) => DropdownMenuItem(
                        value: type,
                        child: Text(type.label),
                      ),
                    )
                    .toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _type = value);
                  }
                },
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: _description,
                minLines: 2,
                maxLines: 4,
                decoration: const InputDecoration(labelText: 'Descrição'),
              ),
              const SizedBox(height: AppSpacing.md),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.sm,
                children: [
                  SizedBox(width: 220, child: _optionalField(_color, 'Cor')),
                  SizedBox(width: 260, child: _optionalField(_icon, 'Ícone')),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              _flag(
                'Recebimento',
                _isReceiving,
                (value) => _isReceiving = value,
              ),
              _flag('Expedição', _isShipping, (value) => _isShipping = value),
              _flag('Armazenagem', _isStorage, (value) => _isStorage = value),
              _flag(
                'Produção',
                _isProduction,
                (value) => _isProduction = value,
              ),
              _flag(
                'Quarentena',
                _isQuarantine,
                (value) => _isQuarantine = value,
              ),
              SwitchListTile(
                value: _isActive,
                title: const Text('Ativa'),
                onChanged: (value) => setState(() => _isActive = value),
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

  TextFormField _optionalField(TextEditingController controller, String label) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
    );
  }

  TextFormField _numberField() {
    return TextFormField(
      controller: _sortOrder,
      keyboardType: TextInputType.number,
      decoration: const InputDecoration(labelText: 'Ordem'),
      validator: (value) {
        final number = int.tryParse(value ?? '');
        return number == null || number < 0 ? 'Ordem inválida' : null;
      },
    );
  }

  SwitchListTile _flag(String title, bool value, ValueChanged<bool> onChanged) {
    return SwitchListTile(
      value: value,
      title: Text(title),
      onChanged: (value) => setState(() => onChanged(value)),
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    setState(() => _saving = true);
    final input = WarehouseZoneInput(
      warehouseId: _warehouseId!,
      code: _code.text.trim().toUpperCase(),
      name: _name.text.trim(),
      description: _emptyAsNull(_description.text),
      type: _type,
      color: _emptyAsNull(_color.text),
      icon: _emptyAsNull(_icon.text),
      sortOrder: int.parse(_sortOrder.text),
      isReceiving: _isReceiving,
      isShipping: _isShipping,
      isStorage: _isStorage,
      isProduction: _isProduction,
      isQuarantine: _isQuarantine,
      isActive: _isActive,
    );
    final controller = ref.read(warehouseZonesControllerProvider.notifier);
    final zone = _isEditing
        ? await controller.updateZone(widget.zoneId!, input)
        : await controller.create(input);
    if (!mounted) {
      return;
    }
    setState(() => _saving = false);
    if (zone != null) {
      context.go('${AppRoutes.warehouseZones}/${zone.id}');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            _message(ref.read(warehouseZonesControllerProvider).error),
          ),
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
    return 'Não foi possível salvar a zona.';
  }
}
