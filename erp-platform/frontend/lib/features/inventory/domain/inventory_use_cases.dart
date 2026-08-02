import 'inventory.dart';
import 'inventory_input.dart';
import 'inventory_repository.dart';

class ListInventoryBalancesUseCase {
  const ListInventoryBalancesUseCase(this._repository);

  final InventoryRepository _repository;

  Future<List<InventoryBalance>> execute({String? productId}) {
    return _repository.listBalances(productId: productId);
  }
}

class ListInventoryMovementsUseCase {
  const ListInventoryMovementsUseCase(this._repository);

  final InventoryRepository _repository;

  Future<List<InventoryMovement>> execute({String? productId}) {
    return _repository.listMovements(productId: productId);
  }
}

class CreateInventoryAdjustmentUseCase {
  const CreateInventoryAdjustmentUseCase(this._repository);

  final InventoryRepository _repository;

  Future<InventoryOperation> execute(InventoryAdjustmentInput input) {
    return _repository.createAdjustment(input);
  }
}

class CreateInventoryReservationUseCase {
  const CreateInventoryReservationUseCase(this._repository);

  final InventoryRepository _repository;

  Future<InventoryOperation> execute(InventoryReservationInput input) {
    return _repository.createReservation(input);
  }
}
