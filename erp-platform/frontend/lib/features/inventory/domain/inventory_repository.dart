import 'inventory.dart';
import 'inventory_input.dart';

abstract interface class InventoryRepository {
  Future<List<InventoryBalance>> listBalances({
    String? productId,
    int page = 1,
    int pageSize = 20,
  });

  Future<List<InventoryMovement>> listMovements({
    String? productId,
    int page = 1,
    int pageSize = 20,
  });

  Future<InventoryOperation> createAdjustment(InventoryAdjustmentInput input);

  Future<InventoryOperation> createReservation(InventoryReservationInput input);
}
