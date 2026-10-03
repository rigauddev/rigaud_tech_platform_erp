import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/restaurant_remote_data_source.dart';
import '../domain/restaurant_table.dart';

final restaurantFloorsProvider = FutureProvider<List<RestaurantFloor>>(
  (ref) => ref.watch(restaurantRemoteDataSourceProvider).floors(),
);
final restaurantTablesProvider =
    FutureProvider.family<List<RestaurantTable>, String?>(
      (ref, floorId) => ref
          .watch(restaurantRemoteDataSourceProvider)
          .tables(floorId: floorId),
    );
