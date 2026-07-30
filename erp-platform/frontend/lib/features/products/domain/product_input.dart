import 'product.dart';

class ProductInput {
  const ProductInput({
    required this.name,
    required this.internalCode,
    required this.productType,
    required this.unitOfMeasure,
    required this.salePrice,
    required this.costPrice,
    required this.isAvailableForSale,
    this.description,
    this.barcode,
    this.mainImageUrl,
  });

  final String name;
  final String internalCode;
  final String? description;
  final String? barcode;
  final ProductType productType;
  final UnitOfMeasure unitOfMeasure;
  final String salePrice;
  final String costPrice;
  final String? mainImageUrl;
  final bool isAvailableForSale;

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'internal_code': internalCode,
      'description': description,
      'barcode': barcode,
      'product_type': productType.apiValue,
      'unit_of_measure': unitOfMeasure.apiValue,
      'sale_price': salePrice,
      'cost_price': costPrice,
      'main_image_url': mainImageUrl,
      'is_available_for_sale': isAvailableForSale,
    };
  }
}
