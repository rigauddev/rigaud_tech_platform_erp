import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/inventory_repository_impl.dart';
import '../domain/inventory.dart';
import '../domain/inventory_input.dart';
import '../domain/inventory_repository.dart';
import '../domain/inventory_use_cases.dart';

final inventoryBalancesControllerProvider =
    AsyncNotifierProvider<InventoryBalancesController, List<InventoryBalance>>(
      InventoryBalancesController.new,
    );

final inventoryMovementsControllerProvider =
    AsyncNotifierProvider<
      InventoryMovementsController,
      List<InventoryMovement>
    >(InventoryMovementsController.new);

class InventoryBalancesController
    extends AsyncNotifier<List<InventoryBalance>> {
  InventoryRepository get _repository => ref.read(inventoryRepositoryProvider);

  @override
  Future<List<InventoryBalance>> build() {
    return ListInventoryBalancesUseCase(_repository).execute();
  }

  Future<void> reload({String? productId}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListInventoryBalancesUseCase(
        _repository,
      ).execute(productId: productId),
    );
  }

  Future<InventoryOperation?> createAdjustment(
    InventoryAdjustmentInput input,
  ) async {
    final result = await AsyncValue.guard(
      () => CreateInventoryAdjustmentUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(inventoryMovementsControllerProvider);
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<InventoryOperation?> createReservation(
    InventoryReservationInput input,
  ) async {
    final result = await AsyncValue.guard(
      () => CreateInventoryReservationUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(inventoryMovementsControllerProvider);
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }
}

class InventoryMovementsController
    extends AsyncNotifier<List<InventoryMovement>> {
  InventoryRepository get _repository => ref.read(inventoryRepositoryProvider);

  @override
  Future<List<InventoryMovement>> build() {
    return ListInventoryMovementsUseCase(_repository).execute();
  }

  Future<void> reload({String? productId}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListInventoryMovementsUseCase(
        _repository,
      ).execute(productId: productId),
    );
  }
}
