import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/config/app_config_provider.dart';
import '../storage/secure_storage.dart';
import '../utils/request_id.dart';
import 'api_error.dart';
import 'api_response.dart';
import 'message_resolver.dart';

final dioProvider = Provider<Dio>((ref) {
  final config = ref.watch(appConfigProvider);

  final dio = Dio(
    BaseOptions(
      baseUrl: config.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      sendTimeout: const Duration(seconds: 10),
      headers: const {'Accept': 'application/json'},
    ),
  );

  dio.interceptors.add(
    _TokenInterceptor(ref.watch(secureStorageProvider), dio),
  );

  if (config.isDevelopment) {
    dio.interceptors.add(LogInterceptor(requestBody: true, responseBody: true));
  }

  return dio;
});

ApiError mapDioError(DioException error) {
  final data = error.response?.data;
  if (data is Map<String, dynamic>) {
    final envelope = ApiEnvelope.fromJson(data);
    return ApiError(
      const MessageResolver().resolve(envelope.code, envelope.message),
      code: envelope.code,
      statusCode: error.response?.statusCode,
      requestId: envelope.requestId,
    );
  }
  return ApiError(
    error.message ?? 'Erro de comunicacao com a API.',
    code: error.type.name,
    statusCode: error.response?.statusCode,
  );
}

class _TokenInterceptor extends Interceptor {
  const _TokenInterceptor(this._storage, this._dio);

  final SecureStorage _storage;
  final Dio _dio;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    options.headers['X-Request-ID'] = createRequestId();
    final accessToken = await _storage.readAccessToken();
    if (accessToken != null &&
        accessToken.isNotEmpty &&
        !_isAuthEndpoint(options.path)) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode != 401 ||
        err.requestOptions.extra['auth_retry'] == true ||
        _isAuthEndpoint(err.requestOptions.path)) {
      handler.next(err);
      return;
    }

    final refreshToken = await _storage.readRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      handler.next(err);
      return;
    }

    try {
      final response = await _dio.post<Map<String, dynamic>>(
        '/api/v1/auth/refresh',
        data: {'refresh_token': refreshToken},
        options: Options(extra: {'auth_retry': true}),
      );
      final data = apiDataObject(response.data);
      final accessToken = data['access_token'] as String? ?? '';
      final newRefreshToken = data['refresh_token'] as String? ?? '';
      if (accessToken.isEmpty || newRefreshToken.isEmpty) {
        await _storage.clearTokens();
        handler.next(err);
        return;
      }

      await _storage.writeTokens(
        accessToken: accessToken,
        refreshToken: newRefreshToken,
      );
      final retryOptions = err.requestOptions;
      retryOptions.extra['auth_retry'] = true;
      retryOptions.headers['Authorization'] = 'Bearer $accessToken';
      final retryResponse = await _dio.fetch<dynamic>(retryOptions);
      handler.resolve(retryResponse);
    } on DioException {
      await _storage.clearTokens();
      handler.next(err);
    }
  }

  bool _isAuthEndpoint(String path) {
    return path.startsWith('/api/v1/auth/login') ||
        path.startsWith('/api/v1/auth/refresh');
  }
}
