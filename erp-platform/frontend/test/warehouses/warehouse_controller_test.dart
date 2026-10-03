import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/features/warehouses/data/warehouse_repository_impl.dart';
import 'package:rigaud_tech_erp/features/warehouses/domain/warehouse.dart';
import 'package:rigaud_tech_erp/features/warehouses/domain/warehouse_input.dart';
import 'package:rigaud_tech_erp/features/warehouses/domain/warehouse_repository.dart';
import 'package:rigaud_tech_erp/features/warehouses/presentation/warehouse_controller.dart';

void main() {
  test('WarehousesController lista e cria depósitos', () async {
    final repository = _FakeWarehouseRepository();
    final container = ProviderContainer(
      overrides: [warehouseRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    final initial = await container.read(warehousesControllerProvider.future);
    expect(initial, isEmpty);

    final created = await container
        .read(warehousesControllerProvider.notifier)
        .create(
          const WarehouseInput(
            code: 'MAIN',
            name: 'Depósito Principal',
            isDefault: true,
            isActive: true,
          ),
        );

    expect(created?.code, 'MAIN');
    expect(container.read(warehousesControllerProvider).value, hasLength(1));
  });
}

class _FakeWarehouseRepository implements WarehouseRepository {
  final List<Warehouse> _items = [];

  @override
  Future<List<Warehouse>> list({
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) async {
    return _items
        .where((item) => isActive == null || item.isActive == isActive)
        .toList();
  }

  @override
  Future<Warehouse> get(String id) async {
    return _items.firstWhere((item) => item.id == id);
  }

  @override
  Future<Warehouse> create(WarehouseInput input) async {
    final warehouse = Warehouse(
      id: 'warehouse-${_items.length + 1}',
      tenantId: 'tenant-1',
      branchId: 'branch-1',
      code: input.code,
      name: input.name,
      description: input.description,
      address: input.address,
      status: input.isActive
          ? WarehouseStatus.active
          : WarehouseStatus.inactive,
      isDefault: input.isDefault,
      isActive: input.isActive,
      createdAt: DateTime.utc(2026, 8, 2),
      updatedAt: DateTime.utc(2026, 8, 2),
    );
    _items.add(warehouse);
    return warehouse;
  }

  @override
  Future<Warehouse> update(String id, WarehouseInput input) async {
    final index = _items.indexWhere((item) => item.id == id);
    final warehouse = await create(input);
    _items[index] = warehouse;
    return warehouse;
  }

  @override
  Future<Warehouse> setDefault(String id) async {
    final warehouse = await get(id);
    return warehouse;
  }

  @override
  Future<Warehouse> delete(String id) async {
    return get(id);
  }
}
