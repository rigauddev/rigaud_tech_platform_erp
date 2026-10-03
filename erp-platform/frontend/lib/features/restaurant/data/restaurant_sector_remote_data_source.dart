import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';

enum RestaurantSectorType { diningRoom, outdoor, bar, vip, counter, other }

class RestaurantSector {
  const RestaurantSector({
    required this.id,
    required this.name,
    required this.code,
    required this.type,
    required this.isActive,
    this.description,
    this.color,
  });
  final String id;
  final String name;
  final String code;
  final RestaurantSectorType type;
  final bool isActive;
  final String? description;
  final String? color;
  factory RestaurantSector.fromJson(Map<String, dynamic> json) =>
      RestaurantSector(
        id: json['id'] as String? ?? '',
        name: json['name'] as String? ?? '',
        code: json['code'] as String? ?? '',
        type: RestaurantSectorType.values.byName(
          _typeName(json['type'] as String? ?? 'other'),
        ),
        isActive: json['is_active'] as bool? ?? false,
        description: json['description'] as String?,
        color: json['color'] as String?,
      );
}

class RestaurantSectorInput {
  const RestaurantSectorInput({
    required this.code,
    required this.name,
    required this.type,
    required this.isActive,
  });
  final String code, name, type;
  final bool isActive;
  Map<String, dynamic> toJson() => {
    'code': code,
    'name': name,
    'type': type,
    'is_active': isActive,
  };
}

String _typeName(String type) => type == 'dining_room' ? 'diningRoom' : type;

class RestaurantSectorRemoteDataSource {
  const RestaurantSectorRemoteDataSource(this._dio);
  final Dio _dio;
  Future<List<RestaurantSector>> list() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/restaurant/sectors',
    );
    return apiDataList(response.data)
        .map((item) => RestaurantSector.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<RestaurantSector> create(RestaurantSectorInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/restaurant/sectors',
      data: input.toJson(),
    );
    return RestaurantSector.fromJson(apiDataObject(response.data));
  }

  Future<RestaurantSector> update(
    String sectorId,
    RestaurantSectorInput input,
  ) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/api/v1/restaurant/sectors/$sectorId',
      data: input.toJson(),
    );
    return RestaurantSector.fromJson(apiDataObject(response.data));
  }
}

final restaurantSectorRemoteDataSourceProvider =
    Provider<RestaurantSectorRemoteDataSource>(
      (ref) => RestaurantSectorRemoteDataSource(ref.watch(dioProvider)),
    );
final restaurantSectorsProvider = FutureProvider<List<RestaurantSector>>(
  (ref) => ref.watch(restaurantSectorRemoteDataSourceProvider).list(),
);
