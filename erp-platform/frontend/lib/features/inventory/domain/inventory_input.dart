import 'inventory.dart';

class InventoryAdjustmentInput {
  const InventoryAdjustmentInput({
    required this.productId,
    required this.adjustmentType,
    required this.quantity,
    required this.reason,
    this.notes,
    this.reasonCode = 'correction',
  });

  final String productId;
  final InventoryAdjustmentType adjustmentType;
  final String quantity;
  final String reason;
  final String? notes;
  final String reasonCode;

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'adjustment_type': adjustmentType.apiValue,
      'quantity': quantity,
      'reason': reason,
      'reason_code': reasonCode,
      if (notes != null && notes!.trim().isNotEmpty) 'notes': notes,
    };
  }
}

class InventoryReservationInput {
  const InventoryReservationInput({
    required this.productId,
    required this.quantity,
    required this.reason,
    this.sourceModule,
  });

  final String productId;
  final String quantity;
  final String reason;
  final String? sourceModule;

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'quantity': quantity,
      'reason': reason,
      if (sourceModule != null && sourceModule!.trim().isNotEmpty)
        'source_module': sourceModule,
    };
  }
}

class PutAwayInput {
  const PutAwayInput({
    required this.documentId,
    required this.productId,
    required this.locationId,
    required this.quantity,
    this.reason,
  });

  final String documentId;
  final String productId;
  final String locationId;
  final String quantity;
  final String? reason;

  Map<String, dynamic> toJson() {
    return {
      'document_id': documentId,
      'product_id': productId,
      'location_id': locationId,
      'quantity': quantity,
      if (reason != null && reason!.trim().isNotEmpty) 'reason': reason,
    };
  }
}

class InventoryTransferInput {
  const InventoryTransferInput({
    required this.code,
    required this.productId,
    required this.sourceWarehouseId,
    required this.targetBranchId,
    required this.targetWarehouseId,
    required this.quantity,
    required this.reason,
  });

  final String code;
  final String productId;
  final String sourceWarehouseId;
  final String targetBranchId;
  final String targetWarehouseId;
  final String quantity;
  final String reason;

  Map<String, dynamic> toJson() => {
    'code': code,
    'product_id': productId,
    'source_warehouse_id': sourceWarehouseId,
    'target_branch_id': targetBranchId,
    'target_warehouse_id': targetWarehouseId,
    'quantity': quantity,
    'reason': reason,
  };
}
