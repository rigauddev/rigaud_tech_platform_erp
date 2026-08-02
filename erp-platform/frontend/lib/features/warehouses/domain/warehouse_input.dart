class WarehouseInput {
  const WarehouseInput({
    required this.code,
    required this.name,
    required this.isDefault,
    required this.isActive,
    this.description,
    this.address,
  });

  final String code;
  final String name;
  final String? description;
  final String? address;
  final bool isDefault;
  final bool isActive;

  Map<String, dynamic> toJson() {
    return {
      'code': code,
      'name': name,
      'description': description,
      'address': address,
      'is_default': isDefault,
      'is_active': isActive,
    };
  }
}
