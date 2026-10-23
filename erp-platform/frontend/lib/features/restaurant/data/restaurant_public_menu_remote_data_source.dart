import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/restaurant_public_menu.dart';

class RestaurantPublicMenuRemoteDataSource {
  const RestaurantPublicMenuRemoteDataSource(this._dio);

  final Dio _dio;

  Future<RestaurantPublicMenu> fetch(String qrCode) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/restaurant/public/menu/${Uri.encodeComponent(qrCode)}',
    );
    return RestaurantPublicMenu.fromJson(apiDataObject(response.data));
  }
}

final restaurantPublicMenuRemoteDataSourceProvider =
    Provider<RestaurantPublicMenuRemoteDataSource>(
      (ref) => RestaurantPublicMenuRemoteDataSource(ref.watch(dioProvider)),
    );

final restaurantPublicMenuProvider =
    FutureProvider.family<RestaurantPublicMenu, String>(
      (ref, qrCode) =>
          ref.watch(restaurantPublicMenuRemoteDataSourceProvider).fetch(qrCode),
    );
