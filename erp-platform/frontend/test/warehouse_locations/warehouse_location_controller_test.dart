import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/features/warehouse_locations/data/warehouse_location_repository_impl.dart';
import 'package:rigaud_tech_erp/features/warehouse_locations/domain/warehouse_location.dart';
import 'package:rigaud_tech_erp/features/warehouse_locations/domain/warehouse_location_input.dart';
import 'package:rigaud_tech_erp/features/warehouse_locations/domain/warehouse_location_repository.dart';
import 'package:rigaud_tech_erp/features/warehouse_locations/presentation/warehouse_location_controller.dart';

void main() {
  test(
    'WarehouseLocationsController lista, cria e ativa localizacoes',
    () async {
      final repository = _FakeWarehouseLocationRepository();
      final container = ProviderContainer(
        overrides: [
          warehouseLocationRepositoryProvider.overrideWithValue(repository),
        ],
      );
      addTearDown(container.dispose);

      final initial = await container.read(
        warehouseLocationsControllerProvider.future,
      );
      expect(initial, isEmpty);

      final created = await container
          .read(warehouseLocationsControllerProvider.notifier)
          .create(
            const WarehouseLocationInput(
              warehouseId: 'warehouse-1',
              zoneId: 'zone-1',
              code: 'A-01',
              name: 'Prateleira A01',
              barcode: 'BAR-A01',
              qrCode: 'rigaud://loc/a01',
              isPickLocation: true,
            ),
          );

      expect(created?.code, 'A-01');
      expect(
        container.read(warehouseLocationsControllerProvider).value,
        hasLength(1),
      );

      await container
          .read(warehouseLocationsControllerProvider.notifier)
          .deactivate(created!.id);
      expect(repository._items.single.isActive, isFalse);

      await container
          .read(warehouseLocationsControllerProvider.notifier)
          .activate(created.id);
      expect(repository._items.single.isActive, isTrue);
    },
  );
}

class _FakeWarehouseLocationRepository implements WarehouseLocationRepository {
  final List<WarehouseLocation> _items = [];

  @override
  Future<List<WarehouseLocation>> list({
    String? warehouseId,
    String? zoneId,
    String? search,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) async {
    return _items
        .where((item) => warehouseId == null || item.warehouseId == warehouseId)
        .where((item) => zoneId == null || item.zoneId == zoneId)
        .where((item) => isActive == null || item.isActive == isActive)
        .where(
          (item) =>
              search == null ||
              item.code.contains(search) ||
              item.name.contains(search),
        )
        .toList();
  }

  @override
  Future<WarehouseLocation> get(String id) async {
    return _items.firstWhere((item) => item.id == id);
  }

  @override
  Future<WarehouseLocation> create(WarehouseLocationInput input) async {
    final location = _build(input, id: 'location-${_items.length + 1}');
    _items.add(location);
    return location;
  }

  @override
  Future<WarehouseLocation> update(
    String id,
    WarehouseLocationInput input,
  ) async {
    final index = _items.indexWhere((item) => item.id == id);
    final updated = _build(input, id: id);
    _items[index] = updated;
    return updated;
  }

  @override
  Future<WarehouseLocation> activate(String id) async {
    final location = await get(id);
    final updated = _copy(location, isActive: true);
    _items[_items.indexWhere((item) => item.id == id)] = updated;
    return updated;
  }

  @override
  Future<WarehouseLocation> deactivate(String id) async {
    final location = await get(id);
    final updated = _copy(location, isActive: false);
    _items[_items.indexWhere((item) => item.id == id)] = updated;
    return updated;
  }

  @override
  Future<WarehouseLocation> reorder(String id, int sortOrder) async {
    final location = await get(id);
    final updated = _copy(location, sortOrder: sortOrder);
    _items[_items.indexWhere((item) => item.id == id)] = updated;
    return updated;
  }

  @override
  Future<WarehouseLocation> delete(String id) async {
    return deactivate(id);
  }

  WarehouseLocation _build(WarehouseLocationInput input, {required String id}) {
    return WarehouseLocation(
      id: id,
      tenantId: 'tenant-1',
      branchId: 'branch-1',
      warehouseId: input.warehouseId,
      zoneId: input.zoneId,
      code: input.code,
      name: input.name,
      alias: input.alias,
      barcode: input.barcode,
      qrCode: input.qrCode,
      aisle: input.aisle,
      rack: input.rack,
      shelf: input.shelf,
      level: input.level,
      position: input.position,
      capacity: input.capacity,
      capacityUnit: input.capacityUnit,
      allowNegative: input.allowNegative,
      allowMixedItems: input.allowMixedItems,
      allowExpired: input.allowExpired,
      isPickLocation: input.isPickLocation,
      isReceiveLocation: input.isReceiveLocation,
      isShippingLocation: input.isShippingLocation,
      isDefault: input.isDefault,
      sortOrder: input.sortOrder,
      status: input.isActive
          ? WarehouseLocationStatus.active
          : WarehouseLocationStatus.inactive,
      isActive: input.isActive,
      createdAt: DateTime.utc(2026, 8, 2),
      updatedAt: DateTime.utc(2026, 8, 2),
    );
  }

  WarehouseLocation _copy(
    WarehouseLocation location, {
    bool? isActive,
    int? sortOrder,
  }) {
    final active = isActive ?? location.isActive;
    return WarehouseLocation(
      id: location.id,
      tenantId: location.tenantId,
      branchId: location.branchId,
      warehouseId: location.warehouseId,
      zoneId: location.zoneId,
      code: location.code,
      name: location.name,
      alias: location.alias,
      barcode: location.barcode,
      qrCode: location.qrCode,
      aisle: location.aisle,
      rack: location.rack,
      shelf: location.shelf,
      level: location.level,
      position: location.position,
      capacity: location.capacity,
      capacityUnit: location.capacityUnit,
      allowNegative: location.allowNegative,
      allowMixedItems: location.allowMixedItems,
      allowExpired: location.allowExpired,
      isPickLocation: location.isPickLocation,
      isReceiveLocation: location.isReceiveLocation,
      isShippingLocation: location.isShippingLocation,
      isDefault: location.isDefault,
      sortOrder: sortOrder ?? location.sortOrder,
      status: active
          ? WarehouseLocationStatus.active
          : WarehouseLocationStatus.inactive,
      isActive: active,
      createdAt: location.createdAt,
      updatedAt: DateTime.utc(2026, 8, 2),
    );
  }
}
