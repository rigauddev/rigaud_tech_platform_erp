import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';

class RestaurantMenuAvailability {
  const RestaurantMenuAvailability({
    required this.id,
    required this.productId,
    required this.serviceDate,
    required this.servicePeriod,
    required this.channels,
    required this.availableQuantity,
    required this.soldQuantity,
    required this.status,
  });

  final String id;
  final String productId;
  final DateTime serviceDate;
  final String servicePeriod;
  final List<String> channels;
  final int? availableQuantity;
  final int soldQuantity;
  final String status;

  factory RestaurantMenuAvailability.fromJson(Map<String, dynamic> json) =>
      RestaurantMenuAvailability(
        id: json['id'] as String,
        productId: json['product_id'] as String,
        serviceDate: DateTime.parse(json['service_date'] as String),
        servicePeriod: json['service_period'] as String,
        channels: (json['channels'] as List<dynamic>? ?? []).cast<String>(),
        availableQuantity: json['available_quantity'] as int?,
        soldQuantity: json['sold_quantity'] as int? ?? 0,
        status: json['status'] as String? ?? 'published',
      );

  int? get remainingQuantity =>
      availableQuantity == null ? null : availableQuantity! - soldQuantity;
}

class RestaurantMenuAvailabilityRemoteDataSource {
  const RestaurantMenuAvailabilityRemoteDataSource(this._dio);
  final Dio _dio;

  Future<List<RestaurantMenuAvailability>> list({DateTime? serviceDate}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/restaurant/menu-availabilities',
      queryParameters: {
        if (serviceDate != null)
          'service_date': serviceDate.toIso8601String().substring(0, 10),
      },
    );
    return apiDataList(response.data)
        .map(
          (item) =>
              RestaurantMenuAvailability.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<void> create({
    required String productId,
    required DateTime serviceDate,
    required String servicePeriod,
    required List<String> channels,
    int? availableQuantity,
  }) async {
    await _dio.post<Map<String, dynamic>>(
      '/api/v1/restaurant/menu-availabilities',
      data: {
        'product_id': productId,
        'service_date': serviceDate.toIso8601String().substring(0, 10),
        'service_period': servicePeriod,
        'channels': channels,
        'available_quantity': availableQuantity,
      },
    );
  }
}

final restaurantMenuAvailabilityRemoteDataSourceProvider =
    Provider<RestaurantMenuAvailabilityRemoteDataSource>(
      (ref) =>
          RestaurantMenuAvailabilityRemoteDataSource(ref.watch(dioProvider)),
    );

final restaurantMenuAvailabilityProvider =
    FutureProvider<List<RestaurantMenuAvailability>>(
      (ref) => ref
          .watch(restaurantMenuAvailabilityRemoteDataSourceProvider)
          .list(serviceDate: DateTime.now()),
    );
