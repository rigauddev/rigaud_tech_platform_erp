import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_error.dart';
import '../data/demo_remote_data_source.dart';
import '../domain/demo_status.dart';

final demoControllerProvider =
    AsyncNotifierProvider<DemoController, DemoStatus?>(DemoController.new);

class DemoController extends AsyncNotifier<DemoStatus?> {
  @override
  Future<DemoStatus?> build() async {
    return ref.watch(demoRemoteDataSourceProvider).status();
  }

  Future<void> install() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(demoRemoteDataSourceProvider).install(),
    );
  }

  Future<void> reset() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(demoRemoteDataSourceProvider).reset(),
    );
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(demoRemoteDataSourceProvider).status(),
    );
  }
}

String demoErrorMessage(Object error) {
  if (error is ApiError) {
    return error.message;
  }
  return 'Não foi possível executar a ação demo.';
}
