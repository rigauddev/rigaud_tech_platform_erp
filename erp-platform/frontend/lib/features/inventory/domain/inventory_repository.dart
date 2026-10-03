import 'inventory.dart';
import 'inventory_input.dart';

abstract interface class InventoryRepository {
  Future<List<InventoryTransfer>> listTransfers({
    int page = 1,
    int pageSize = 20,
  });
  Future<List<InventoryCount>> listCounts({int page = 1, int pageSize = 20});
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

  Future<List<InventoryMovement>> listTransactions({
    String? productId,
    String? warehouseId,
    String? locationId,
    String? movementType,
    String? originModule,
    String? businessProcess,
    String? sourceModule,
    int page = 1,
    int pageSize = 20,
  });

  Future<InventoryOperation> createAdjustment(InventoryAdjustmentInput input);

  Future<InventoryOperation> createReservation(InventoryReservationInput input);

  Future<PutAwayOperation> confirmPutAway(PutAwayInput input);

  Future<InventoryTransfer> createTransfer(InventoryTransferInput input);

  Future<InventoryTransfer> dispatchTransfer(String transferId);

  Future<InventoryTransfer> receiveTransfer(String transferId);
}
