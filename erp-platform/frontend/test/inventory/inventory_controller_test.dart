import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/features/inventory/data/inventory_repository_impl.dart';
import 'package:rigaud_tech_erp/features/inventory/domain/inventory.dart';
import 'package:rigaud_tech_erp/features/inventory/domain/inventory_input.dart';
import 'package:rigaud_tech_erp/features/inventory/domain/inventory_repository.dart';
import 'package:rigaud_tech_erp/features/inventory/presentation/inventory_controller.dart';

void main() {
  test('InventoryBalancesController lista saldos e registra ajuste', () async {
    final repository = _FakeInventoryRepository();
    final container = ProviderContainer(
      overrides: [inventoryRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    final initial = await container.read(
      inventoryBalancesControllerProvider.future,
    );
    expect(initial, isEmpty);

    final operation = await container
        .read(inventoryBalancesControllerProvider.notifier)
        .createAdjustment(
          const InventoryAdjustmentInput(
            productId: 'product-1',
            adjustmentType: InventoryAdjustmentType.increase,
            quantity: '5',
            reason: 'Entrada inicial',
          ),
        );

    expect(operation?.balance.availableQuantity, '5.000');
    expect(
      container.read(inventoryBalancesControllerProvider).value,
      hasLength(1),
    );

    final putaway = await container
        .read(inventoryBalancesControllerProvider.notifier)
        .confirmPutAway(
          const PutAwayInput(
            documentId: 'document-1',
            productId: 'product-1',
            locationId: 'location-1',
            quantity: '5.000',
            reason: 'Endereçamento',
          ),
        );

    expect(putaway?.documentStatus, 'available');
    expect(putaway?.movement.businessProcess, 'PUTAWAY');
    expect(
      container.read(inventoryBalancesControllerProvider).value,
      hasLength(2),
    );
  });
}

class _FakeInventoryRepository implements InventoryRepository {
  final List<InventoryBalance> _balances = [];
  final List<InventoryMovement> _movements = [];

  @override
  Future<List<InventoryBalance>> listBalances({
    String? productId,
    int page = 1,
    int pageSize = 20,
  }) async {
    return _balances;
  }

  @override
  Future<List<InventoryMovement>> listMovements({
    String? productId,
    int page = 1,
    int pageSize = 20,
  }) async {
    return _movements;
  }

  @override
  Future<InventoryOperation> createAdjustment(
    InventoryAdjustmentInput input,
  ) async {
    final balance = InventoryBalance(
      id: 'balance-1',
      tenantId: 'tenant-1',
      branchId: 'branch-1',
      productId: input.productId,
      physicalQuantity: '5.000',
      reservedQuantity: '0.000',
      putawayPendingQuantity: '0.000',
      availableQuantity: '5.000',
      createdAt: DateTime.utc(2026, 8, 1),
      updatedAt: DateTime.utc(2026, 8, 1),
    );
    final movement = InventoryMovement(
      id: 'movement-1',
      productId: input.productId,
      movementType: 'adjustment_in',
      physicalQuantityDelta: '5.000',
      reservedQuantityDelta: '0.000',
      putawayPendingQuantityDelta: '0.000',
      originModule: 'ADJUSTMENT',
      businessProcess: 'ADJUSTMENT',
      reason: input.reason,
      eventName: 'inventory.adjusted.in',
      createdAt: DateTime.utc(2026, 8, 1),
    );
    _balances
      ..clear()
      ..add(balance);
    _movements.add(movement);
    return InventoryOperation(balance: balance, movement: movement);
  }

  @override
  Future<InventoryOperation> createReservation(
    InventoryReservationInput input,
  ) async {
    final balance = _balances.first;
    final movement = InventoryMovement(
      id: 'movement-2',
      productId: input.productId,
      movementType: 'reservation_created',
      physicalQuantityDelta: '0.000',
      reservedQuantityDelta: input.quantity,
      putawayPendingQuantityDelta: '0.000',
      originModule: 'RESERVATION',
      businessProcess: 'RESERVATION',
      reason: input.reason,
      eventName: 'inventory.reserved',
      createdAt: DateTime.utc(2026, 8, 1),
    );
    _movements.add(movement);
    return InventoryOperation(balance: balance, movement: movement);
  }

  @override
  Future<PutAwayOperation> confirmPutAway(PutAwayInput input) async {
    final source = InventoryBalance(
      id: 'source-balance',
      tenantId: 'tenant-1',
      branchId: 'branch-1',
      productId: input.productId,
      warehouseId: 'warehouse-1',
      physicalQuantity: '0.000',
      reservedQuantity: '0.000',
      putawayPendingQuantity: '0.000',
      availableQuantity: '0.000',
      createdAt: DateTime.utc(2026, 8, 1),
      updatedAt: DateTime.utc(2026, 8, 1),
    );
    final target = InventoryBalance(
      id: 'target-balance',
      tenantId: 'tenant-1',
      branchId: 'branch-1',
      productId: input.productId,
      warehouseId: 'warehouse-1',
      locationId: input.locationId,
      physicalQuantity: input.quantity,
      reservedQuantity: '0.000',
      putawayPendingQuantity: '0.000',
      availableQuantity: input.quantity,
      createdAt: DateTime.utc(2026, 8, 1),
      updatedAt: DateTime.utc(2026, 8, 1),
    );
    final movement = InventoryMovement(
      id: 'movement-putaway',
      productId: input.productId,
      movementType: 'putaway',
      physicalQuantityDelta: '0.000',
      reservedQuantityDelta: '0.000',
      putawayPendingQuantityDelta: '-${input.quantity}',
      originModule: 'PURCHASE',
      businessProcess: 'PUTAWAY',
      reason: input.reason ?? 'Put Away',
      eventName: 'inventory.putaway.confirmed',
      createdAt: DateTime.utc(2026, 8, 1),
    );
    _balances
      ..clear()
      ..addAll([source, target]);
    _movements.add(movement);
    return PutAwayOperation(
      documentId: input.documentId,
      documentStatus: 'available',
      sourceBalance: source,
      targetBalance: target,
      movement: movement,
    );
  }
}
