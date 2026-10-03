enum RestaurantTableStatus {
  available,
  occupied,
  reserved,
  orderPending,
  kitchen,
  waitingPayment,
  cleaning,
  blocked;

  String get label => switch (this) {
    available => 'Disponível',
    occupied => 'Ocupada',
    reserved => 'Reservada',
    orderPending => 'Pedido pendente',
    kitchen => 'Em preparo',
    waitingPayment => 'Aguardando pagamento',
    cleaning => 'Em limpeza',
    blocked => 'Bloqueada',
  };
}

enum RestaurantTableShape { square, round, rectangle }

class RestaurantFloor {
  const RestaurantFloor({
    required this.id,
    required this.code,
    required this.name,
    required this.isActive,
    this.description,
    this.sortOrder = 0,
  });
  final String id;
  final String code;
  final String name;
  final String? description;
  final int sortOrder;
  final bool isActive;
  factory RestaurantFloor.fromJson(Map<String, dynamic> json) =>
      RestaurantFloor(
        id: json['id'] as String? ?? '',
        code: json['code'] as String? ?? '',
        name: json['name'] as String? ?? '',
        description: json['description'] as String?,
        sortOrder: json['sort_order'] as int? ?? 0,
        isActive: json['is_active'] as bool? ?? false,
      );
}

class RestaurantTable {
  const RestaurantTable({
    required this.id,
    required this.floorId,
    required this.number,
    required this.capacity,
    required this.positionX,
    required this.positionY,
    required this.width,
    required this.height,
    required this.shape,
    required this.status,
    required this.isActive,
    this.name,
    this.qrCode,
  });
  final String id;
  final String floorId;
  final String number;
  final String? name;
  final int capacity;
  final double positionX;
  final double positionY;
  final double width;
  final double height;
  final RestaurantTableShape shape;
  final RestaurantTableStatus status;
  final String? qrCode;
  final bool isActive;
  factory RestaurantTable.fromJson(Map<String, dynamic> json) =>
      RestaurantTable(
        id: json['id'] as String? ?? '',
        floorId: json['floor_id'] as String? ?? '',
        number: json['number'] as String? ?? '',
        name: json['name'] as String?,
        capacity: json['capacity'] as int? ?? 0,
        positionX: double.tryParse('${json['position_x']}') ?? 0,
        positionY: double.tryParse('${json['position_y']}') ?? 0,
        width: double.tryParse('${json['width']}') ?? 96,
        height: double.tryParse('${json['height']}') ?? 72,
        shape: RestaurantTableShape.values.byName(
          json['shape'] as String? ?? 'square',
        ),
        status: RestaurantTableStatus.values.byName(
          _enumName(json['status'] as String? ?? 'available'),
        ),
        qrCode: json['qr_code'] as String?,
        isActive: json['is_active'] as bool? ?? false,
      );
}

String _enumName(String value) => switch (value) {
  'order_pending' => 'orderPending',
  'waiting_payment' => 'waitingPayment',
  _ => value,
};
