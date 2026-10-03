import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';

class RestaurantStaff {
  const RestaurantStaff({
    required this.id,
    required this.name,
    required this.code,
    required this.role,
    required this.status,
    this.sectorId,
  });
  final String id;
  final String name;
  final String code;
  final String role;
  final String status;
  final String? sectorId;

  factory RestaurantStaff.fromJson(Map<String, dynamic> json) =>
      RestaurantStaff(
        id: json['id'] as String,
        name: json['name'] as String,
        code: json['code'] as String,
        role: json['role'] as String,
        status: json['status'] as String,
        sectorId: json['sector_id'] as String?,
      );
}

class RestaurantStaffRemoteDataSource {
  const RestaurantStaffRemoteDataSource(this._dio);
  final Dio _dio;
  Future<List<RestaurantStaff>> list({String? search}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/restaurant/staff',
      queryParameters: search == null || search.isEmpty
          ? null
          : {'search': search},
    );
    return apiDataList(response.data)
        .map((item) => RestaurantStaff.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> create({required String code, required String name}) async {
    await _dio.post<Map<String, dynamic>>(
      '/api/v1/restaurant/staff',
      data: {
        'code': code,
        'name': name,
        'role': 'waiter',
        'status': 'available',
      },
    );
  }
}

final restaurantStaffRemoteDataSourceProvider =
    Provider<RestaurantStaffRemoteDataSource>(
      (ref) => RestaurantStaffRemoteDataSource(ref.watch(dioProvider)),
    );
final restaurantStaffProvider = FutureProvider<List<RestaurantStaff>>(
  (ref) => ref.watch(restaurantStaffRemoteDataSourceProvider).list(),
);
