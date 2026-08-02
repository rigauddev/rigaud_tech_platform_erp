import 'inventory.dart';

class InventoryAdjustmentInput {
  const InventoryAdjustmentInput({
    required this.productId,
    required this.adjustmentType,
    required this.quantity,
    required this.reason,
    this.notes,
  });

  final String productId;
  final InventoryAdjustmentType adjustmentType;
  final String quantity;
  final String reason;
  final String? notes;

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'adjustment_type': adjustmentType.apiValue,
      'quantity': quantity,
      'reason': reason,
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
