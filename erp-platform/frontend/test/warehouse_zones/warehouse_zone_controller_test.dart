import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/features/warehouse_zones/data/warehouse_zone_repository_impl.dart';
import 'package:rigaud_tech_erp/features/warehouse_zones/domain/warehouse_zone.dart';
import 'package:rigaud_tech_erp/features/warehouse_zones/domain/warehouse_zone_input.dart';
import 'package:rigaud_tech_erp/features/warehouse_zones/domain/warehouse_zone_repository.dart';
import 'package:rigaud_tech_erp/features/warehouse_zones/presentation/warehouse_zone_controller.dart';

void main() {
  test('WarehouseZonesController lista, cria e reordena zonas', () async {
    final repository = _FakeWarehouseZoneRepository();
    final container = ProviderContainer(
      overrides: [
        warehouseZoneRepositoryProvider.overrideWithValue(repository),
      ],
    );
    addTearDown(container.dispose);

    final initial = await container.read(
      warehouseZonesControllerProvider.future,
    );
    expect(initial, isEmpty);

    final created = await container
        .read(warehouseZonesControllerProvider.notifier)
        .create(
          const WarehouseZoneInput(
            warehouseId: 'warehouse-1',
            code: 'REC',
            name: 'Recebimento',
            type: WarehouseZoneType.receiving,
            sortOrder: 10,
            isReceiving: true,
            isShipping: false,
            isStorage: false,
            isProduction: false,
            isQuarantine: false,
            isActive: true,
          ),
        );

    expect(created?.code, 'REC');
    expect(
      container.read(warehouseZonesControllerProvider).value,
      hasLength(1),
    );

    await container
        .read(warehouseZonesControllerProvider.notifier)
        .reorder(created!.id, 30);

    expect(repository._items.single.sortOrder, 30);
  });
}

class _FakeWarehouseZoneRepository implements WarehouseZoneRepository {
  final List<WarehouseZone> _items = [];

  @override
  Future<List<WarehouseZone>> list({
    String? warehouseId,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) async {
    return _items
        .where((item) => warehouseId == null || item.warehouseId == warehouseId)
        .where((item) => isActive == null || item.isActive == isActive)
        .toList();
  }

  @override
  Future<WarehouseZone> get(String id) async {
    return _items.firstWhere((item) => item.id == id);
  }

  @override
  Future<WarehouseZone> create(WarehouseZoneInput input) async {
    final zone = WarehouseZone(
      id: 'zone-${_items.length + 1}',
      tenantId: 'tenant-1',
      branchId: 'branch-1',
      warehouseId: input.warehouseId,
      code: input.code,
      name: input.name,
      description: input.description,
      type: input.type,
      color: input.color,
      icon: input.icon,
      sortOrder: input.sortOrder,
      isReceiving: input.isReceiving,
      isShipping: input.isShipping,
      isStorage: input.isStorage,
      isProduction: input.isProduction,
      isQuarantine: input.isQuarantine,
      status: input.isActive
          ? WarehouseZoneStatus.active
          : WarehouseZoneStatus.inactive,
      isActive: input.isActive,
      createdAt: DateTime.utc(2026, 8, 2),
      updatedAt: DateTime.utc(2026, 8, 2),
    );
    _items.add(zone);
    return zone;
  }

  @override
  Future<WarehouseZone> update(String id, WarehouseZoneInput input) async {
    final index = _items.indexWhere((item) => item.id == id);
    final zone = await create(input);
    _items[index] = zone;
    _items.removeLast();
    return zone;
  }

  @override
  Future<WarehouseZone> reorder(String id, int sortOrder) async {
    final zone = await get(id);
    final index = _items.indexWhere((item) => item.id == id);
    final updated = WarehouseZone(
      id: zone.id,
      tenantId: zone.tenantId,
      branchId: zone.branchId,
      warehouseId: zone.warehouseId,
      code: zone.code,
      name: zone.name,
      description: zone.description,
      type: zone.type,
      color: zone.color,
      icon: zone.icon,
      sortOrder: sortOrder,
      isReceiving: zone.isReceiving,
      isShipping: zone.isShipping,
      isStorage: zone.isStorage,
      isProduction: zone.isProduction,
      isQuarantine: zone.isQuarantine,
      status: zone.status,
      isActive: zone.isActive,
      createdAt: zone.createdAt,
      updatedAt: DateTime.utc(2026, 8, 2),
    );
    _items[index] = updated;
    return updated;
  }

  @override
  Future<WarehouseZone> delete(String id) async {
    return get(id);
  }
}
