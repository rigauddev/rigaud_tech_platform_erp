import 'warehouse_zone.dart';

class WarehouseZoneInput {
  const WarehouseZoneInput({
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
    required this.isActive,
    this.description,
    this.color,
    this.icon,
  });

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
  final bool isActive;

  Map<String, dynamic> toJson() {
    return {
      'warehouse_id': warehouseId,
      'code': code,
      'name': name,
      'description': description,
      'type': type.name,
      'color': color,
      'icon': icon,
      'sort_order': sortOrder,
      'is_receiving': isReceiving,
      'is_shipping': isShipping,
      'is_storage': isStorage,
      'is_production': isProduction,
      'is_quarantine': isQuarantine,
      'is_active': isActive,
    };
  }
}
