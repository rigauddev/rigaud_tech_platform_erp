class RestaurantPublicMenu {
  const RestaurantPublicMenu({
    required this.restaurantName,
    required this.currency,
    required this.tableNumber,
    required this.serviceDate,
    required this.items,
    this.tableName,
  });

  final String restaurantName;
  final String currency;
  final String tableNumber;
  final String? tableName;
  final DateTime serviceDate;
  final List<RestaurantPublicMenuItem> items;

  factory RestaurantPublicMenu.fromJson(Map<String, dynamic> json) =>
      RestaurantPublicMenu(
        restaurantName: json['restaurant_name'] as String,
        currency: json['currency'] as String,
        tableNumber: json['table_number'] as String,
        tableName: json['table_name'] as String?,
        serviceDate: DateTime.parse(json['service_date'] as String),
        items: (json['items'] as List<dynamic>)
            .map(
              (item) => RestaurantPublicMenuItem.fromJson(
                item as Map<String, dynamic>,
              ),
            )
            .toList(),
      );
}

class RestaurantPublicMenuItem {
  const RestaurantPublicMenuItem({
    required this.name,
    required this.salePrice,
    required this.servicePeriod,
    required this.isAvailable,
    this.description,
    this.imageUrl,
  });

  final String name;
  final String? description;
  final String salePrice;
  final String? imageUrl;
  final String servicePeriod;
  final bool isAvailable;

  factory RestaurantPublicMenuItem.fromJson(Map<String, dynamic> json) =>
      RestaurantPublicMenuItem(
        name: json['name'] as String,
        description: json['description'] as String?,
        salePrice: (json['sale_price'] ?? '0.00').toString(),
        imageUrl: json['image_url'] as String?,
        servicePeriod: json['service_period'] as String,
        isAvailable: json['is_available'] as bool? ?? false,
      );
}
