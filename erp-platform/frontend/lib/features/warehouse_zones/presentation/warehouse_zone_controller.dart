import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/warehouse_zone_repository_impl.dart';
import '../domain/warehouse_zone.dart';
import '../domain/warehouse_zone_input.dart';
import '../domain/warehouse_zone_repository.dart';
import '../domain/warehouse_zone_use_cases.dart';

final warehouseZonesControllerProvider =
    AsyncNotifierProvider<WarehouseZonesController, List<WarehouseZone>>(
      WarehouseZonesController.new,
    );

final warehouseZoneDetailsProvider =
    FutureProvider.family<WarehouseZone, String>((ref, id) {
      return GetWarehouseZoneUseCase(
        ref.watch(warehouseZoneRepositoryProvider),
      ).execute(id);
    });

class WarehouseZonesController extends AsyncNotifier<List<WarehouseZone>> {
  WarehouseZoneRepository get _repository =>
      ref.read(warehouseZoneRepositoryProvider);

  @override
  Future<List<WarehouseZone>> build() {
    return ListWarehouseZonesUseCase(_repository).execute();
  }

  Future<void> reload({String? warehouseId, bool? isActive}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListWarehouseZonesUseCase(
        _repository,
      ).execute(warehouseId: warehouseId, isActive: isActive),
    );
  }

  Future<WarehouseZone?> create(WarehouseZoneInput input) async {
    final result = await AsyncValue.guard(
      () => CreateWarehouseZoneUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<WarehouseZone?> updateZone(String id, WarehouseZoneInput input) async {
    final result = await AsyncValue.guard(
      () => UpdateWarehouseZoneUseCase(_repository).execute(id, input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(warehouseZoneDetailsProvider(id));
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<void> reorder(String id, int sortOrder) {
    return _change(id, () => _repository.reorder(id, sortOrder));
  }

  Future<void> deleteZone(String id) =>
      _change(id, () => _repository.delete(id));

  Future<void> toggleActive(WarehouseZone zone) {
    return _change(
      zone.id,
      () => _repository.update(
        zone.id,
        WarehouseZoneInput(
          warehouseId: zone.warehouseId,
          code: zone.code,
          name: zone.name,
          description: zone.description,
          type: zone.type,
          color: zone.color,
          icon: zone.icon,
          sortOrder: zone.sortOrder,
          isReceiving: zone.isReceiving,
          isShipping: zone.isShipping,
          isStorage: zone.isStorage,
          isProduction: zone.isProduction,
          isQuarantine: zone.isQuarantine,
          isActive: !zone.isActive,
        ),
      ),
    );
  }

  Future<void> _change(
    String id,
    Future<WarehouseZone> Function() action,
  ) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
      ref.invalidate(warehouseZoneDetailsProvider(id));
    } else {
      state = AsyncError(result.error!, result.stackTrace!);
    }
  }
}
