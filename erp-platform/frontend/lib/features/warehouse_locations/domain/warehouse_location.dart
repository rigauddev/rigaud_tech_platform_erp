enum WarehouseLocationStatus {
  active,
  inactive;

  String get label {
    return switch (this) {
      WarehouseLocationStatus.active => 'Ativa',
      WarehouseLocationStatus.inactive => 'Inativa',
    };
  }
}

class WarehouseLocation {
  const WarehouseLocation({
    required this.id,
    required this.tenantId,
    required this.branchId,
    required this.warehouseId,
    required this.zoneId,
    required this.code,
    required this.name,
    required this.allowNegative,
    required this.allowMixedItems,
    required this.allowExpired,
    required this.isPickLocation,
    required this.isReceiveLocation,
    required this.isShippingLocation,
    required this.isDefault,
    required this.sortOrder,
    required this.status,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.alias,
    this.barcode,
    this.qrCode,
    this.aisle,
    this.rack,
    this.shelf,
    this.level,
    this.position,
    this.capacity,
    this.capacityUnit,
  });

  final String id;
  final String tenantId;
  final String branchId;
  final String warehouseId;
  final String zoneId;
  final String code;
  final String name;
  final String? alias;
  final String? barcode;
  final String? qrCode;
  final String? aisle;
  final String? rack;
  final String? shelf;
  final String? level;
  final String? position;
  final double? capacity;
  final String? capacityUnit;
  final bool allowNegative;
  final bool allowMixedItems;
  final bool allowExpired;
  final bool isPickLocation;
  final bool isReceiveLocation;
  final bool isShippingLocation;
  final bool isDefault;
  final int sortOrder;
  final WarehouseLocationStatus status;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory WarehouseLocation.fromJson(Map<String, dynamic> json) {
    return WarehouseLocation(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      branchId: json['branch_id'] as String? ?? '',
      warehouseId: json['warehouse_id'] as String? ?? '',
      zoneId: json['zone_id'] as String? ?? '',
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      alias: json['alias'] as String?,
      barcode: json['barcode'] as String?,
      qrCode: json['qr_code'] as String?,
      aisle: json['aisle'] as String?,
      rack: json['rack'] as String?,
      shelf: json['shelf'] as String?,
      level: json['level'] as String?,
      position: json['position'] as String?,
      capacity: _toDouble(json['capacity']),
      capacityUnit: json['capacity_unit'] as String?,
      allowNegative: json['allow_negative'] as bool? ?? false,
      allowMixedItems: json['allow_mixed_items'] as bool? ?? true,
      allowExpired: json['allow_expired'] as bool? ?? false,
      isPickLocation: json['is_pick_location'] as bool? ?? false,
      isReceiveLocation: json['is_receive_location'] as bool? ?? false,
      isShippingLocation: json['is_shipping_location'] as bool? ?? false,
      isDefault: json['is_default'] as bool? ?? false,
      sortOrder: json['sort_order'] as int? ?? 0,
      status: WarehouseLocationStatus.values.byName(
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

double? _toDouble(Object? value) {
  if (value == null) {
    return null;
  }
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value.toString());
}
