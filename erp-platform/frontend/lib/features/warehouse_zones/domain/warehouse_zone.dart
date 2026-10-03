enum WarehouseZoneStatus {
  active,
  inactive;

  String get label {
    return switch (this) {
      WarehouseZoneStatus.active => 'Ativa',
      WarehouseZoneStatus.inactive => 'Inativa',
    };
  }
}

enum WarehouseZoneType {
  receiving,
  shipping,
  storage,
  production,
  quarantine,
  picking,
  display,
  other;

  String get label {
    return switch (this) {
      WarehouseZoneType.receiving => 'Recebimento',
      WarehouseZoneType.shipping => 'Expedição',
      WarehouseZoneType.storage => 'Armazenagem',
      WarehouseZoneType.production => 'Produção',
      WarehouseZoneType.quarantine => 'Quarentena',
      WarehouseZoneType.picking => 'Picking',
      WarehouseZoneType.display => 'Vitrine',
      WarehouseZoneType.other => 'Outra',
    };
  }
}

class WarehouseZone {
  const WarehouseZone({
    required this.id,
    required this.tenantId,
    required this.branchId,
    required this.warehouseId,
    required this.code,
    required this.name,
    required this.type,
    required this.sortOrder,
    required this.isReceiving,
    required this.isShipping,
    required this.isStorage,
    required this.isProduction,
    required this.isQuarantine,
    required this.status,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.description,
    this.color,
    this.icon,
  });

  final String id;
  final String tenantId;
  final String branchId;
  final String warehouseId;
  final String code;
  final String name;
  final String? description;
  final WarehouseZoneType type;
  final String? color;
  final String? icon;
  final int sortOrder;
  final bool isReceiving;
  final bool isShipping;
  final bool isStorage;
  final bool isProduction;
  final bool isQuarantine;
  final WarehouseZoneStatus status;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory WarehouseZone.fromJson(Map<String, dynamic> json) {
    return WarehouseZone(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      branchId: json['branch_id'] as String? ?? '',
      warehouseId: json['warehouse_id'] as String? ?? '',
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      type: WarehouseZoneType.values.byName(
        json['type'] as String? ?? 'storage',
      ),
      color: json['color'] as String?,
      icon: json['icon'] as String?,
      sortOrder: json['sort_order'] as int? ?? 0,
      isReceiving: json['is_receiving'] as bool? ?? false,
      isShipping: json['is_shipping'] as bool? ?? false,
      isStorage: json['is_storage'] as bool? ?? false,
      isProduction: json['is_production'] as bool? ?? false,
      isQuarantine: json['is_quarantine'] as bool? ?? false,
      status: WarehouseZoneStatus.values.byName(
        json['status'] as String? ?? 'inactive',
      ),
      isActive: json['is_active'] as bool? ?? false,
      createdAt:
          DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
      updatedAt:
          DateTime.tryParse(json['updated_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
    );
  }
}
