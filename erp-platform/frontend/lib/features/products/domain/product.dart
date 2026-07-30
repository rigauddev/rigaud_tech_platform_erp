enum ProductType {
  simple,
  service,
  preparedItem;

  String get apiValue {
    return switch (this) {
      ProductType.simple => 'simple',
      ProductType.service => 'service',
      ProductType.preparedItem => 'prepared_item',
    };
  }

  String get label {
    return switch (this) {
      ProductType.simple => 'Simples',
      ProductType.service => 'Serviço',
      ProductType.preparedItem => 'Preparado',
    };
  }

  static ProductType fromApi(String value) {
    return ProductType.values.firstWhere(
      (type) => type.apiValue == value,
      orElse: () => ProductType.simple,
    );
  }
}

enum UnitOfMeasure {
  unit,
  kg,
  g,
  l,
  ml,
  portion;

  String get apiValue => name;

  String get label {
    return switch (this) {
      UnitOfMeasure.unit => 'Unidade',
      UnitOfMeasure.kg => 'Quilograma',
      UnitOfMeasure.g => 'Grama',
      UnitOfMeasure.l => 'Litro',
      UnitOfMeasure.ml => 'Mililitro',
      UnitOfMeasure.portion => 'Porção',
    };
  }
}

enum ProductStatus {
  active,
  inactive;

  String get label {
    return switch (this) {
      ProductStatus.active => 'Ativo',
      ProductStatus.inactive => 'Inativo',
    };
  }
}

class Product {
  const Product({
    required this.id,
    required this.tenantId,
    required this.name,
    required this.internalCode,
    required this.productType,
    required this.unitOfMeasure,
    required this.status,
    required this.salePrice,
    required this.costPrice,
    required this.isActive,
    required this.isAvailableForSale,
    required this.createdAt,
    required this.updatedAt,
    this.description,
    this.barcode,
    this.mainImageUrl,
  });

  final String id;
  final String tenantId;
  final String name;
  final String? description;
  final String internalCode;
  final String? barcode;
  final ProductType productType;
  final UnitOfMeasure unitOfMeasure;
  final ProductStatus status;
  final String salePrice;
  final String costPrice;
  final String? mainImageUrl;
  final bool isActive;
  final bool isAvailableForSale;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      internalCode: json['internal_code'] as String? ?? '',
      barcode: json['barcode'] as String?,
      productType: ProductType.fromApi(json['product_type'] as String? ?? ''),
      unitOfMeasure: UnitOfMeasure.values.byName(
        json['unit_of_measure'] as String? ?? 'unit',
      ),
      status: ProductStatus.values.byName(
        json['status'] as String? ?? 'inactive',
      ),
      salePrice: (json['sale_price'] ?? '0.00').toString(),
      costPrice: (json['cost_price'] ?? '0.00').toString(),
      mainImageUrl: json['main_image_url'] as String?,
      isActive: json['is_active'] as bool? ?? false,
      isAvailableForSale: json['is_available_for_sale'] as bool? ?? false,
      createdAt:
          DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
      updatedAt:
          DateTime.tryParse(json['updated_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
    );
  }

  String get formattedSalePrice {
    final value = double.tryParse(salePrice) ?? 0;
    return 'R\$ ${value.toStringAsFixed(2).replaceAll('.', ',')}';
  }
}
