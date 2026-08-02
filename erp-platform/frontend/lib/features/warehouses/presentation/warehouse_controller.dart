import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/warehouse_repository_impl.dart';
import '../domain/warehouse.dart';
import '../domain/warehouse_input.dart';
import '../domain/warehouse_repository.dart';
import '../domain/warehouse_use_cases.dart';

final warehousesControllerProvider =
    AsyncNotifierProvider<WarehousesController, List<Warehouse>>(
      WarehousesController.new,
    );

final warehouseDetailsProvider = FutureProvider.family<Warehouse, String>((
  ref,
  id,
) {
  return GetWarehouseUseCase(
    ref.watch(warehouseRepositoryProvider),
  ).execute(id);
});

class WarehousesController extends AsyncNotifier<List<Warehouse>> {
  WarehouseRepository get _repository => ref.read(warehouseRepositoryProvider);

  @override
  Future<List<Warehouse>> build() {
    return ListWarehousesUseCase(_repository).execute();
  }

  Future<void> reload({bool? isActive}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListWarehousesUseCase(_repository).execute(isActive: isActive),
    );
  }

  Future<Warehouse?> create(WarehouseInput input) async {
    final result = await AsyncValue.guard(
      () => CreateWarehouseUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<Warehouse?> updateWarehouse(String id, WarehouseInput input) async {
    final result = await AsyncValue.guard(
      () => UpdateWarehouseUseCase(_repository).execute(id, input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(warehouseDetailsProvider(id));
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<void> setDefault(String id) =>
      _change(id, () => _repository.setDefault(id));

  Future<void> deleteWarehouse(String id) =>
      _change(id, () => _repository.delete(id));

  Future<void> toggleActive(Warehouse warehouse) {
    return _change(
      warehouse.id,
      () => _repository.update(
        warehouse.id,
        WarehouseInput(
          code: warehouse.code,
          name: warehouse.name,
          description: warehouse.description,
          address: warehouse.address,
          isDefault: warehouse.isActive ? false : warehouse.isDefault,
          isActive: !warehouse.isActive,
        ),
      ),
    );
  }

  Future<void> _change(String id, Future<Warehouse> Function() action) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
      ref.invalidate(warehouseDetailsProvider(id));
    } else {
      state = AsyncError(result.error!, result.stackTrace!);
    }
  }
}
