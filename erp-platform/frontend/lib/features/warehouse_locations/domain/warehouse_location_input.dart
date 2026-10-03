class WarehouseLocationInput {
  const WarehouseLocationInput({
    required this.warehouseId,
    required this.zoneId,
    required this.code,
    required this.name,
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
    this.allowNegative = false,
    this.allowMixedItems = true,
    this.allowExpired = false,
    this.isPickLocation = false,
    this.isReceiveLocation = false,
    this.isShippingLocation = false,
    this.isDefault = false,
    this.sortOrder = 0,
    this.isActive = true,
  });

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
  final bool isActive;

  Map<String, dynamic> toJson() {
    return {
      'warehouse_id': warehouseId,
      'zone_id': zoneId,
      'code': code,
      'name': name,
      if (alias != null) 'alias': alias,
      if (barcode != null) 'barcode': barcode,
      if (qrCode != null) 'qr_code': qrCode,
      if (aisle != null) 'aisle': aisle,
      if (rack != null) 'rack': rack,
      if (shelf != null) 'shelf': shelf,
      if (level != null) 'level': level,
      if (position != null) 'position': position,
      if (capacity != null) 'capacity': capacity,
      if (capacityUnit != null) 'capacity_unit': capacityUnit,
      'allow_negative': allowNegative,
      'allow_mixed_items': allowMixedItems,
      'allow_expired': allowExpired,
      'is_pick_location': isPickLocation,
      'is_receive_location': isReceiveLocation,
      'is_shipping_location': isShippingLocation,
      'is_default': isDefault,
      'sort_order': sortOrder,
      'is_active': isActive,
    };
  }
}
