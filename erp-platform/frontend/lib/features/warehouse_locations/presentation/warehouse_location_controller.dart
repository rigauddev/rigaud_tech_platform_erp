import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/warehouse_location_repository_impl.dart';
import '../domain/warehouse_location.dart';
import '../domain/warehouse_location_input.dart';
import '../domain/warehouse_location_repository.dart';
import '../domain/warehouse_location_use_cases.dart';

final warehouseLocationsControllerProvider =
    AsyncNotifierProvider<
      WarehouseLocationsController,
      List<WarehouseLocation>
    >(WarehouseLocationsController.new);

final warehouseLocationDetailsProvider =
    FutureProvider.family<WarehouseLocation, String>((ref, id) {
      return GetWarehouseLocationUseCase(
        ref.watch(warehouseLocationRepositoryProvider),
      ).execute(id);
    });

class WarehouseLocationsController
    extends AsyncNotifier<List<WarehouseLocation>> {
  WarehouseLocationRepository get _repository =>
      ref.read(warehouseLocationRepositoryProvider);

  @override
  Future<List<WarehouseLocation>> build() {
    return ListWarehouseLocationsUseCase(_repository).execute();
  }

  Future<void> reload({
    String? warehouseId,
    String? zoneId,
    String? search,
    bool? isActive,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListWarehouseLocationsUseCase(_repository).execute(
        warehouseId: warehouseId,
        zoneId: zoneId,
        search: search,
        isActive: isActive,
      ),
    );
  }

  Future<WarehouseLocation?> create(WarehouseLocationInput input) async {
    final result = await AsyncValue.guard(
      () => CreateWarehouseLocationUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<WarehouseLocation?> updateLocation(
    String id,
    WarehouseLocationInput input,
  ) async {
    final result = await AsyncValue.guard(
      () => UpdateWarehouseLocationUseCase(_repository).execute(id, input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(warehouseLocationDetailsProvider(id));
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<void> activate(String id) {
    return _change(id, () => _repository.activate(id));
  }

  Future<void> deactivate(String id) {
    return _change(id, () => _repository.deactivate(id));
  }

  Future<void> reorder(String id, int sortOrder) {
    return _change(id, () => _repository.reorder(id, sortOrder));
  }

  Future<void> deleteLocation(String id) {
    return _change(id, () => _repository.delete(id));
  }

  Future<void> _change(
    String id,
    Future<WarehouseLocation> Function() action,
  ) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
      ref.invalidate(warehouseLocationDetailsProvider(id));
    } else {
      state = AsyncError(result.error!, result.stackTrace!);
    }
  }
}
