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
    required this.reason,
    required this.eventName,
    required this.createdAt,
  });

  final String id;
  final String productId;
  final String movementType;
  final String physicalQuantityDelta;
  final String reservedQuantityDelta;
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
      reason: json['reason'] as String? ?? '',
      eventName: json['event_name'] as String? ?? '',
      createdAt:
          DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
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
