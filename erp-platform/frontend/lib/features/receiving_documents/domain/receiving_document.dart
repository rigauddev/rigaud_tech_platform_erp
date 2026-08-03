enum ReceivingDocumentStatus {
  draft,
  expected,
  receiving,
  partial,
  received,
  putawayPending,
  cancelled;

  String get label {
    return switch (this) {
      ReceivingDocumentStatus.draft => 'Rascunho',
      ReceivingDocumentStatus.expected => 'Esperado',
      ReceivingDocumentStatus.receiving => 'Recebendo',
      ReceivingDocumentStatus.partial => 'Parcial',
      ReceivingDocumentStatus.received => 'Recebido',
      ReceivingDocumentStatus.putawayPending => 'Put away pendente',
      ReceivingDocumentStatus.cancelled => 'Cancelado',
    };
  }

  String get apiValue {
    return switch (this) {
      ReceivingDocumentStatus.putawayPending => 'putaway_pending',
      _ => name,
    };
  }

  static ReceivingDocumentStatus fromApi(String value) {
    return switch (value) {
      'putaway_pending' => ReceivingDocumentStatus.putawayPending,
      _ => ReceivingDocumentStatus.values.firstWhere(
        (status) => status.name == value,
        orElse: () => ReceivingDocumentStatus.draft,
      ),
    };
  }
}

class ReceivingItem {
  const ReceivingItem({
    required this.id,
    required this.tenantId,
    required this.productId,
    required this.orderedQuantity,
    required this.receivedQuantity,
    required this.damagedQuantity,
    required this.pendingQuantity,
    required this.unitCost,
    this.documentId,
  });

  final String id;
  final String tenantId;
  final String? documentId;
  final String productId;
  final double orderedQuantity;
  final double receivedQuantity;
  final double damagedQuantity;
  final double pendingQuantity;
  final double unitCost;

  factory ReceivingItem.fromJson(Map<String, dynamic> json) {
    return ReceivingItem(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      documentId: json['document_id'] as String?,
      productId: json['product_id'] as String? ?? '',
      orderedQuantity: _toDouble(json['ordered_quantity']),
      receivedQuantity: _toDouble(json['received_quantity']),
      damagedQuantity: _toDouble(json['damaged_quantity']),
      pendingQuantity: _toDouble(json['pending_quantity']),
      unitCost: _toDouble(json['unit_cost']),
    );
  }
}

class ReceivingDocument {
  const ReceivingDocument({
    required this.id,
    required this.tenantId,
    required this.branchId,
    required this.warehouseId,
    required this.documentNumber,
    required this.documentType,
    required this.status,
    required this.items,
    required this.createdAt,
    required this.updatedAt,
    this.supplierId,
    this.expectedDate,
    this.receivedDate,
    this.notes,
  });

  final String id;
  final String tenantId;
  final String branchId;
  final String warehouseId;
  final String? supplierId;
  final String documentNumber;
  final String documentType;
  final ReceivingDocumentStatus status;
  final DateTime? expectedDate;
  final DateTime? receivedDate;
  final String? notes;
  final List<ReceivingItem> items;
  final DateTime createdAt;
  final DateTime updatedAt;

  double get orderedTotal {
    return items.fold(0, (total, item) => total + item.orderedQuantity);
  }

  double get pendingTotal {
    return items.fold(0, (total, item) => total + item.pendingQuantity);
  }

  factory ReceivingDocument.fromJson(Map<String, dynamic> json) {
    return ReceivingDocument(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      branchId: json['branch_id'] as String? ?? '',
      warehouseId: json['warehouse_id'] as String? ?? '',
      supplierId: json['supplier_id'] as String?,
      documentNumber: json['document_number'] as String? ?? '',
      documentType: json['document_type'] as String? ?? '',
      status: ReceivingDocumentStatus.fromApi(
        json['status'] as String? ?? 'draft',
      ),
      expectedDate: _toDate(json['expected_date']),
      receivedDate: _toDate(json['received_date']),
      notes: json['notes'] as String?,
      items: (json['items'] as List<dynamic>? ?? const [])
          .map((item) => ReceivingItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      createdAt:
          _toDate(json['created_at']) ?? DateTime.fromMillisecondsSinceEpoch(0),
      updatedAt:
          _toDate(json['updated_at']) ?? DateTime.fromMillisecondsSinceEpoch(0),
    );
  }
}

double _toDouble(Object? value) {
  if (value == null) {
    return 0;
  }
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value.toString()) ?? 0;
}

DateTime? _toDate(Object? value) {
  if (value == null) {
    return null;
  }
  return DateTime.tryParse(value.toString());
}
