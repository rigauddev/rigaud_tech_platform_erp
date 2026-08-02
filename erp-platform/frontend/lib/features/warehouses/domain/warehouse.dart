enum WarehouseStatus {
  active,
  inactive;

  String get label {
    return switch (this) {
      WarehouseStatus.active => 'Ativo',
      WarehouseStatus.inactive => 'Inativo',
    };
  }
}

class Warehouse {
  const Warehouse({
    required this.id,
    required this.tenantId,
    required this.branchId,
    required this.code,
    required this.name,
    required this.status,
    required this.isDefault,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.description,
    this.address,
  });

  final String id;
  final String tenantId;
  final String branchId;
  final String code;
  final String name;
  final String? description;
  final String? address;
  final WarehouseStatus status;
  final bool isDefault;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory Warehouse.fromJson(Map<String, dynamic> json) {
    return Warehouse(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      branchId: json['branch_id'] as String? ?? '',
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      address: json['address'] as String?,
      status: WarehouseStatus.values.byName(
        json['status'] as String? ?? 'inactive',
      ),
      isDefault: json['is_default'] as bool? ?? false,
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
