class CategoryInput {
  const CategoryInput({
    required this.name,
    required this.internalCode,
    required this.displayOrder,
    this.parentId,
    this.slug,
    this.description,
    this.icon,
    this.color,
  });

  final String name;
  final String internalCode;
  final String? parentId;
  final String? slug;
  final String? description;
  final String? icon;
  final String? color;
  final int displayOrder;

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'internal_code': internalCode,
      'parent_id': parentId,
      'slug': slug,
      'description': description,
      'icon': icon,
      'color': color,
      'display_order': displayOrder,
    };
  }
}
