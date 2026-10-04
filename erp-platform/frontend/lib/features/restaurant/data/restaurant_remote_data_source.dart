import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/restaurant_table.dart';

class RestaurantRemoteDataSource {
  const RestaurantRemoteDataSource(this._dio);
  final Dio _dio;
  Future<List<RestaurantFloor>> floors() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/restaurant/floors',
    );
    return apiDataList(response.data)
        .map((item) => RestaurantFloor.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<RestaurantTable>> tables({String? floorId}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/restaurant/tables',
      queryParameters: {'floor_id': ?floorId},
    );
    return apiDataList(response.data)
        .map((item) => RestaurantTable.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<RestaurantTable> generateQrCode(String tableId) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/restaurant/tables/$tableId/qr-code',
    );
    return RestaurantTable.fromJson(apiDataObject(response.data));
  }
}

final restaurantRemoteDataSourceProvider = Provider<RestaurantRemoteDataSource>(
  (ref) => RestaurantRemoteDataSource(ref.watch(dioProvider)),
);
