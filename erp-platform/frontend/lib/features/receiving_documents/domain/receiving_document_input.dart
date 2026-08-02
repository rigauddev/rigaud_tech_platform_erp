import 'receiving_document.dart';

class ReceivingItemInput {
  const ReceivingItemInput({
    required this.productId,
    required this.orderedQuantity,
    this.receivedQuantity = 0,
    this.damagedQuantity = 0,
    this.unitCost = 0,
  });

  final String productId;
  final double orderedQuantity;
  final double receivedQuantity;
  final double damagedQuantity;
  final double unitCost;

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'ordered_quantity': orderedQuantity,
      'received_quantity': receivedQuantity,
      'damaged_quantity': damagedQuantity,
      'unit_cost': unitCost,
    };
  }
}

class ReceivingDocumentInput {
  const ReceivingDocumentInput({
    required this.warehouseId,
    required this.documentNumber,
    required this.documentType,
    required this.status,
    required this.items,
    this.supplierId,
    this.expectedDate,
    this.receivedDate,
    this.notes,
  });

  final String warehouseId;
  final String? supplierId;
  final String documentNumber;
  final String documentType;
  final ReceivingDocumentStatus status;
  final DateTime? expectedDate;
  final DateTime? receivedDate;
  final String? notes;
  final List<ReceivingItemInput> items;

  Map<String, dynamic> toJson() {
    return {
      'warehouse_id': warehouseId,
      'supplier_id': supplierId,
      'document_number': documentNumber,
      'document_type': documentType,
      'status': status.name,
      'expected_date': expectedDate?.toIso8601String(),
      'received_date': receivedDate?.toIso8601String(),
      'notes': notes,
      'items': items.map((item) => item.toJson()).toList(),
    };
  }
}

class ReceivingStatusInput {
  const ReceivingStatusInput({required this.status, this.receivedDate});

  final ReceivingDocumentStatus status;
  final DateTime? receivedDate;

  Map<String, dynamic> toJson() {
    return {
      'status': status.name,
      'received_date': receivedDate?.toIso8601String(),
    };
  }
}
