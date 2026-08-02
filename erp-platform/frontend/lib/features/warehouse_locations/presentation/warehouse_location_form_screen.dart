import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../../warehouse_zones/domain/warehouse_zone.dart';
import '../../warehouse_zones/presentation/warehouse_zone_controller.dart';
import '../../warehouses/domain/warehouse.dart';
import '../../warehouses/presentation/warehouse_controller.dart';
import '../domain/warehouse_location.dart';
import '../domain/warehouse_location_input.dart';
import 'warehouse_location_controller.dart';

class WarehouseLocationFormScreen extends ConsumerStatefulWidget {
  const WarehouseLocationFormScreen({this.locationId, super.key});

  final String? locationId;

  @override
  ConsumerState<WarehouseLocationFormScreen> createState() =>
      _WarehouseLocationFormScreenState();
}

class _WarehouseLocationFormScreenState
    extends ConsumerState<WarehouseLocationFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _code = TextEditingController();
  final _name = TextEditingController();
  final _alias = TextEditingController();
  final _barcode = TextEditingController();
  final _qrCode = TextEditingController();
  final _aisle = TextEditingController();
  final _rack = TextEditingController();
  final _shelf = TextEditingController();
  final _level = TextEditingController();
  final _position = TextEditingController();
  final _capacity = TextEditingController();
  final _capacityUnit = TextEditingController();
  final _sortOrder = TextEditingController(text: '0');
  String? _warehouseId;
  String? _zoneId;
  bool _allowNegative = false;
  bool _allowMixedItems = true;
  bool _allowExpired = false;
  bool _isPickLocation = false;
  bool _isReceiveLocation = false;
  bool _isShippingLocation = false;
  bool _isDefault = false;
  bool _isActive = true;
  bool _hydrated = false;
  bool _saving = false;

  bool get _isEditing => widget.locationId != null;

  @override
  void dispose() {
    for (final controller in [
      _code,
      _name,
      _alias,
      _barcode,
      _qrCode,
      _aisle,
      _rack,
      _shelf,
      _level,
      _position,
      _capacity,
      _capacityUnit,
      _sortOrder,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final details = _isEditing
        ? ref.watch(warehouseLocationDetailsProvider(widget.locationId!))
        : null;
    details?.whenData(_hydrate);
    final warehouses = ref.watch(warehousesControllerProvider);
    final zones = ref.watch(warehouseZonesControllerProvider);
    return AppScaffold(
      title: _isEditing ? 'Editar localização' : 'Nova localização',
      body: warehouses.when(
        data: (warehouseItems) => zones.when(
          data: (zoneItems) =>
              details?.when(
                data: (_) => _buildForm(context, warehouseItems, zoneItems),
                error: (error, stackTrace) =>
                    Center(child: Text(_message(error))),
                loading: () => const Center(child: CircularProgressIndicator()),
              ) ??
              _buildForm(context, warehouseItems, zoneItems),
          error: (error, stackTrace) => Center(child: Text(_message(error))),
          loading: () => const Center(child: CircularProgressIndicator()),
        ),
        error: (error, stackTrace) => Center(child: Text(_message(error))),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  void _hydrate(WarehouseLocation location) {
    if (_hydrated) {
      return;
    }
    _warehouseId = location.warehouseId;
    _zoneId = location.zoneId;
    _code.text = location.code;
    _name.text = location.name;
    _alias.text = location.alias ?? '';
    _barcode.text = location.barcode ?? '';
    _qrCode.text = location.qrCode ?? '';
    _aisle.text = location.aisle ?? '';
    _rack.text = location.rack ?? '';
    _shelf.text = location.shelf ?? '';
    _level.text = location.level ?? '';
    _position.text = location.position ?? '';
    _capacity.text = location.capacity?.toString() ?? '';
    _capacityUnit.text = location.capacityUnit ?? '';
    _sortOrder.text = location.sortOrder.toString();
    _allowNegative = location.allowNegative;
    _allowMixedItems = location.allowMixedItems;
    _allowExpired = location.allowExpired;
    _isPickLocation = location.isPickLocation;
    _isReceiveLocation = location.isReceiveLocation;
    _isShippingLocation = location.isShippingLocation;
    _isDefault = location.isDefault;
    _isActive = location.isActive;
    _hydrated = true;
  }

  Widget _buildForm(
    BuildContext context,
    List<Warehouse> warehouses,
    List<WarehouseZone> zones,
  ) {
    final activeWarehouses = warehouses
        .where((warehouse) => warehouse.isActive)
        .toList();
    final activeZones = zones
        .where((zone) => zone.isActive)
        .where(
          (zone) => _warehouseId == null || zone.warehouseId == _warehouseId,
        )
        .toList();
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Form(
        key: _formKey,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 920),
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
                      onChanged: (value) => setState(() {
                        _warehouseId = value;
                        _zoneId = null;
                      }),
                      validator: _required,
                    ),
                  ),
                  SizedBox(
                    width: 300,
                    child: DropdownButtonFormField<String>(
                      initialValue: _zoneId,
                      decoration: const InputDecoration(labelText: 'Zona'),
                      items: activeZones
                          .map(
                            (zone) => DropdownMenuItem(
                              value: zone.id,
                              child: Text('${zone.name} · ${zone.code}'),
                            ),
                          )
                          .toList(),
                      onChanged: (value) => setState(() => _zoneId = value),
                      validator: _required,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  SizedBox(width: 180, child: _field(_code, 'Código')),
                  SizedBox(width: 320, child: _field(_name, 'Nome')),
                  SizedBox(
                    width: 220,
                    child: _optionalField(_alias, 'Apelido'),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  SizedBox(
                    width: 220,
                    child: _optionalField(_barcode, 'Código de barras'),
                  ),
                  SizedBox(
                    width: 320,
                    child: _optionalField(_qrCode, 'QR Code'),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  SizedBox(
                    width: 120,
                    child: _optionalField(_aisle, 'Corredor'),
                  ),
                  SizedBox(width: 120, child: _optionalField(_rack, 'Rack')),
                  SizedBox(
                    width: 120,
                    child: _optionalField(_shelf, 'Prateleira'),
                  ),
                  SizedBox(width: 120, child: _optionalField(_level, 'Nível')),
                  SizedBox(
                    width: 120,
                    child: _optionalField(_position, 'Posição'),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              Wrap(
                spacing: AppSpacing.md,
                runSpacing: AppSpacing.md,
                children: [
                  SizedBox(
                    width: 160,
                    child: _decimalField(_capacity, 'Capacidade'),
                  ),
                  SizedBox(
                    width: 140,
                    child: _optionalField(_capacityUnit, 'Unidade'),
                  ),
                  SizedBox(width: 120, child: _numberField()),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              _flag(
                'Permite saldo negativo',
                _allowNegative,
                (value) => _allowNegative = value,
              ),
              _flag(
                'Permite itens mistos',
                _allowMixedItems,
                (value) => _allowMixedItems = value,
              ),
              _flag(
                'Permite vencidos',
                _allowExpired,
                (value) => _allowExpired = value,
              ),
              _flag(
                'Picking',
                _isPickLocation,
                (value) => _isPickLocation = value,
              ),
              _flag(
                'Recebimento',
                _isReceiveLocation,
                (value) => _isReceiveLocation = value,
              ),
              _flag(
                'Expedição',
                _isShippingLocation,
                (value) => _isShippingLocation = value,
              ),
              _flag('Padrão', _isDefault, (value) => _isDefault = value),
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
      validator: _required,
    );
  }

  TextFormField _optionalField(TextEditingController controller, String label) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
    );
  }

  TextFormField _decimalField(TextEditingController controller, String label) {
    return TextFormField(
      controller: controller,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(labelText: label),
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return null;
        }
        final number = double.tryParse(value.replaceAll(',', '.'));
        return number == null || number < 0 ? 'Valor inválido' : null;
      },
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
    final input = WarehouseLocationInput(
      warehouseId: _warehouseId!,
      zoneId: _zoneId!,
      code: _code.text.trim().toUpperCase(),
      name: _name.text.trim(),
      alias: _emptyAsNull(_alias.text),
      barcode: _emptyAsNull(_barcode.text),
      qrCode: _emptyAsNull(_qrCode.text),
      aisle: _emptyAsNull(_aisle.text),
      rack: _emptyAsNull(_rack.text),
      shelf: _emptyAsNull(_shelf.text),
      level: _emptyAsNull(_level.text),
      position: _emptyAsNull(_position.text),
      capacity: _emptyAsDouble(_capacity.text),
      capacityUnit: _emptyAsNull(_capacityUnit.text),
      allowNegative: _allowNegative,
      allowMixedItems: _allowMixedItems,
      allowExpired: _allowExpired,
      isPickLocation: _isPickLocation,
      isReceiveLocation: _isReceiveLocation,
      isShippingLocation: _isShippingLocation,
      isDefault: _isDefault,
      sortOrder: int.parse(_sortOrder.text),
      isActive: _isActive,
    );
    final controller = ref.read(warehouseLocationsControllerProvider.notifier);
    final location = _isEditing
        ? await controller.updateLocation(widget.locationId!, input)
        : await controller.create(input);
    if (!mounted) {
      return;
    }
    setState(() => _saving = false);
    if (location != null) {
      context.go('${AppRoutes.warehouseLocations}/${location.id}');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            _message(ref.read(warehouseLocationsControllerProvider).error),
          ),
        ),
      );
    }
  }

  String? _required(String? value) {
    return value == null || value.trim().isEmpty ? 'Campo obrigatório' : null;
  }

  String? _emptyAsNull(String value) {
    final trimmed = value.trim();
    return trimmed.isEmpty ? null : trimmed;
  }

  double? _emptyAsDouble(String value) {
    final trimmed = value.trim().replaceAll(',', '.');
    return trimmed.isEmpty ? null : double.parse(trimmed);
  }

  String _message(Object? error) {
    final text = error.toString();
    if (text.contains('requestId')) {
      return text;
    }
    return 'Não foi possível salvar a localização.';
  }
}
