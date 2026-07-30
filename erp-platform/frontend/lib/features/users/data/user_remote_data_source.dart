import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/user.dart';
import '../domain/user_input.dart';

class UserRemoteDataSource {
  const UserRemoteDataSource(this._dio);

  final Dio _dio;

  Future<UserPage> list({
    int page = 1,
    int pageSize = 20,
    String? companyId,
    UserStatus? status,
    String? search,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/users',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (companyId != null && companyId.isNotEmpty) 'company_id': companyId,
        if (status != null) 'status': status.name,
        if (search != null && search.isNotEmpty) 'search': search,
      },
    );
    final envelope = ApiEnvelope.fromJson(response.data ?? {});
    return UserPage(
      items: apiDataList(response.data)
          .map((item) => UserProfile.fromJson(item as Map<String, dynamic>))
          .toList(),
      total: envelope.meta?.total ?? 0,
      page: envelope.meta?.page ?? page,
      pageSize: envelope.meta?.pageSize ?? pageSize,
    );
  }

  Future<UserProfile> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/users/$id');
    return UserProfile.fromJson(apiDataObject(response.data));
  }

  Future<UserProfile> me() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/users/me');
    return UserProfile.fromJson(apiDataObject(response.data));
  }

  Future<UserProfile> create(UserCreateInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/users',
      data: input.toJson(),
    );
    return UserProfile.fromJson(apiDataObject(response.data));
  }

  Future<UserProfile> update(String id, UserUpdateInput input) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/api/v1/users/$id',
      data: input.toJson(),
    );
    return UserProfile.fromJson(apiDataObject(response.data));
  }

  Future<UserProfile> updateMe(ProfileUpdateInput input) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/api/v1/users/me',
      data: input.toJson(),
    );
    return UserProfile.fromJson(apiDataObject(response.data));
  }

  Future<UserProfile> activate(String id) => _statusAction(id, 'activate');

  Future<UserProfile> deactivate(String id) => _statusAction(id, 'deactivate');

  Future<UserProfile> block(String id) => _statusAction(id, 'block');

  Future<UserProfile> unblock(String id) => _statusAction(id, 'unblock');

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await _dio.post<Map<String, dynamic>>(
      '/api/v1/users/me/change-password',
      data: {'current_password': currentPassword, 'new_password': newPassword},
    );
  }

  Future<void> resetPassword({
    required String id,
    required String temporaryPassword,
  }) async {
    await _dio.post<Map<String, dynamic>>(
      '/api/v1/users/$id/reset-password',
      data: {'temporary_password': temporaryPassword},
    );
  }

  Future<UserProfile> _statusAction(String id, String action) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/users/$id/$action',
    );
    return UserProfile.fromJson(apiDataObject(response.data));
  }
}

final userRemoteDataSourceProvider = Provider<UserRemoteDataSource>((ref) {
  return UserRemoteDataSource(ref.watch(dioProvider));
});
