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

final inventoryTransactionsControllerProvider =
    AsyncNotifierProvider<
      InventoryTransactionsController,
      List<InventoryMovement>
    >(InventoryTransactionsController.new);

final inventoryCountsControllerProvider =
    AsyncNotifierProvider<InventoryCountsController, List<InventoryCount>>(
      InventoryCountsController.new,
    );

final inventoryTransfersControllerProvider =
    AsyncNotifierProvider<
      InventoryTransfersController,
      List<InventoryTransfer>
    >(InventoryTransfersController.new);

class InventoryTransfersController
    extends AsyncNotifier<List<InventoryTransfer>> {
  InventoryRepository get _repository => ref.read(inventoryRepositoryProvider);

  @override
  Future<List<InventoryTransfer>> build() => _repository.listTransfers();

  Future<void> reload() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_repository.listTransfers);
  }

  Future<InventoryTransfer?> create(InventoryTransferInput input) async {
    final result = await AsyncValue.guard(
      () => _repository.createTransfer(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<InventoryTransfer?> dispatch(String transferId) =>
      _transition(() => _repository.dispatchTransfer(transferId));

  Future<InventoryTransfer?> receive(String transferId) =>
      _transition(() => _repository.receiveTransfer(transferId));

  Future<InventoryTransfer?> _transition(
    Future<InventoryTransfer> Function() action,
  ) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
      ref.invalidate(inventoryBalancesControllerProvider);
      ref.invalidate(inventoryMovementsControllerProvider);
      ref.invalidate(inventoryTransactionsControllerProvider);
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }
}

class InventoryCountsController extends AsyncNotifier<List<InventoryCount>> {
  @override
  Future<List<InventoryCount>> build() =>
      ref.read(inventoryRepositoryProvider).listCounts();
  Future<void> reload() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(inventoryRepositoryProvider).listCounts(),
    );
  }
}

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
      ref.invalidate(inventoryTransactionsControllerProvider);
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
      ref.invalidate(inventoryTransactionsControllerProvider);
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<PutAwayOperation?> confirmPutAway(PutAwayInput input) async {
    final result = await AsyncValue.guard(
      () => ConfirmPutAwayUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(inventoryMovementsControllerProvider);
      ref.invalidate(inventoryTransactionsControllerProvider);
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }
}

class InventoryTransactionsController
    extends AsyncNotifier<List<InventoryMovement>> {
  InventoryRepository get _repository => ref.read(inventoryRepositoryProvider);

  @override
  Future<List<InventoryMovement>> build() {
    return ListInventoryTransactionsUseCase(_repository).execute();
  }

  Future<void> reload({
    String? productId,
    String? warehouseId,
    String? locationId,
    String? movementType,
    String? originModule,
    String? businessProcess,
    String? sourceModule,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListInventoryTransactionsUseCase(_repository).execute(
        productId: productId,
        warehouseId: warehouseId,
        locationId: locationId,
        movementType: movementType,
        originModule: originModule,
        businessProcess: businessProcess,
        sourceModule: sourceModule,
      ),
    );
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
