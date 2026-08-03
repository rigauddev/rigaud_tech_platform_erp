enum InventoryAdjustmentType {
  increase,
  decrease;

  String get apiValue => name;

  String get label {
    return switch (this) {
      InventoryAdjustmentType.increase => 'Entrada',
      InventoryAdjustmentType.decrease => 'Saída',
    };
  }
}

class InventoryBalance {
  const InventoryBalance({
    required this.id,
    required this.tenantId,
    required this.branchId,
    required this.productId,
    required this.physicalQuantity,
    required this.reservedQuantity,
    required this.putawayPendingQuantity,
    required this.availableQuantity,
    required this.createdAt,
    required this.updatedAt,
    this.warehouseId,
    this.locationId,
  });

  final String id;
  final String tenantId;
  final String branchId;
  final String productId;
  final String? warehouseId;
  final String? locationId;
  final String physicalQuantity;
  final String reservedQuantity;
  final String putawayPendingQuantity;
  final String availableQuantity;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory InventoryBalance.fromJson(Map<String, dynamic> json) {
    return InventoryBalance(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      branchId: json['branch_id'] as String? ?? '',
      productId: json['product_id'] as String? ?? '',
      warehouseId: json['warehouse_id'] as String?,
      locationId: json['location_id'] as String?,
      physicalQuantity: (json['physical_quantity'] ?? '0.000').toString(),
      reservedQuantity: (json['reserved_quantity'] ?? '0.000').toString(),
      putawayPendingQuantity: (json['putaway_pending_quantity'] ?? '0.000')
          .toString(),
      availableQuantity: (json['available_quantity'] ?? '0.000').toString(),
      createdAt:
          DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
      updatedAt:
          DateTime.tryParse(json['updated_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
    );
  }
}

class InventoryMovement {
  const InventoryMovement({
    required this.id,
    required this.productId,
    required this.movementType,
    required this.physicalQuantityDelta,
    required this.reservedQuantityDelta,
    required this.putawayPendingQuantityDelta,
    required this.originModule,
    required this.businessProcess,
    required this.reason,
    required this.eventName,
    required this.createdAt,
  });

  final String id;
  final String productId;
  final String movementType;
  final String physicalQuantityDelta;
  final String reservedQuantityDelta;
  final String putawayPendingQuantityDelta;
  final String originModule;
  final String businessProcess;
  final String reason;
  final String eventName;
  final DateTime createdAt;

  factory InventoryMovement.fromJson(Map<String, dynamic> json) {
    return InventoryMovement(
      id: json['id'] as String? ?? '',
      productId: json['product_id'] as String? ?? '',
      movementType: json['movement_type'] as String? ?? '',
      physicalQuantityDelta: (json['physical_quantity_delta'] ?? '0.000')
          .toString(),
      reservedQuantityDelta: (json['reserved_quantity_delta'] ?? '0.000')
          .toString(),
      putawayPendingQuantityDelta:
          (json['putaway_pending_quantity_delta'] ?? '0.000').toString(),
      originModule: json['origin_module'] as String? ?? '',
      businessProcess: json['business_process'] as String? ?? '',
      reason: json['reason'] as String? ?? '',
      eventName: json['event_name'] as String? ?? '',
      createdAt:
          DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
    );
  }
}

class PutAwayOperation {
  const PutAwayOperation({
    required this.documentId,
    required this.documentStatus,
    required this.sourceBalance,
    required this.targetBalance,
    required this.movement,
  });

  final String documentId;
  final String documentStatus;
  final InventoryBalance sourceBalance;
  final InventoryBalance targetBalance;
  final InventoryMovement movement;

  factory PutAwayOperation.fromJson(Map<String, dynamic> json) {
    return PutAwayOperation(
      documentId: json['document_id'] as String? ?? '',
      documentStatus: json['document_status'] as String? ?? '',
      sourceBalance: InventoryBalance.fromJson(
        json['source_balance'] as Map<String, dynamic>? ?? {},
      ),
      targetBalance: InventoryBalance.fromJson(
        json['target_balance'] as Map<String, dynamic>? ?? {},
      ),
      movement: InventoryMovement.fromJson(
        json['movement'] as Map<String, dynamic>? ?? {},
      ),
    );
  }
}

class InventoryOperation {
  const InventoryOperation({required this.balance, required this.movement});

  final InventoryBalance balance;
  final InventoryMovement movement;

  factory InventoryOperation.fromJson(Map<String, dynamic> json) {
    return InventoryOperation(
      balance: InventoryBalance.fromJson(
        json['balance'] as Map<String, dynamic>? ?? {},
      ),
      movement: InventoryMovement.fromJson(
        json['movement'] as Map<String, dynamic>? ?? {},
      ),
    );
  }
}
