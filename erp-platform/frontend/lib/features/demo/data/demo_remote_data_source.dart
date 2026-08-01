import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/demo_status.dart';

class DemoRemoteDataSource {
  const DemoRemoteDataSource(this._dio);

  final Dio _dio;

  Future<DemoStatus> status() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/demo/status',
    );
    return DemoStatus.fromJson(apiDataObject(response.data));
  }

  Future<DemoStatus> install() async {
    await _dio.get<Map<String, dynamic>>('/api/v1/demo/install');
    return status();
  }

  Future<DemoStatus> reset() async {
    await _dio.get<Map<String, dynamic>>('/api/v1/demo/reset');
    return status();
  }

  Future<Map<String, dynamic>> scenarios() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/demo/scenarios',
    );
    return apiDataObject(response.data);
  }
}

final demoRemoteDataSourceProvider = Provider<DemoRemoteDataSource>((ref) {
  return DemoRemoteDataSource(ref.watch(dioProvider));
});
