enum CategoryStatus {
  active,
  inactive;

  String get label {
    return switch (this) {
      CategoryStatus.active => 'Ativa',
      CategoryStatus.inactive => 'Inativa',
    };
  }
}

class Category {
  const Category({
    required this.id,
    required this.tenantId,
    required this.internalCode,
    required this.name,
    required this.slug,
    required this.displayOrder,
    required this.status,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.parentId,
    this.description,
    this.icon,
    this.color,
    this.children = const [],
  });

  final String id;
  final String tenantId;
  final String? parentId;
  final String internalCode;
  final String name;
  final String slug;
  final String? description;
  final String? icon;
  final String? color;
  final int displayOrder;
  final CategoryStatus status;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<Category> children;

  factory Category.fromJson(Map<String, dynamic> json) {
    final childrenJson = (json['children'] as List<dynamic>? ?? const []);
    return Category(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      parentId: json['parent_id'] as String?,
      internalCode: json['internal_code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      slug: json['slug'] as String? ?? '',
      description: json['description'] as String?,
      icon: json['icon'] as String?,
      color: json['color'] as String?,
      displayOrder: json['display_order'] as int? ?? 0,
      status: CategoryStatus.values.byName(
        json['status'] as String? ?? 'inactive',
      ),
      isActive: json['is_active'] as bool? ?? false,
      createdAt:
          DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
      updatedAt:
          DateTime.tryParse(json['updated_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
      children: childrenJson
          .map((item) => Category.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}
