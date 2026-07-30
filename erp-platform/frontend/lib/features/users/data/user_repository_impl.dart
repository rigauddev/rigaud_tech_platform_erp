import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../domain/user.dart';
import '../domain/user_input.dart';
import '../domain/user_repository.dart';
import 'user_remote_data_source.dart';

class UserRepositoryImpl implements UserRepository {
  const UserRepositoryImpl(this._remoteDataSource);

  final UserRemoteDataSource _remoteDataSource;

  @override
  Future<UserPage> list({
    int page = 1,
    int pageSize = 20,
    String? companyId,
    UserStatus? status,
    String? search,
  }) {
    return _guard(
      () => _remoteDataSource.list(
        page: page,
        pageSize: pageSize,
        companyId: companyId,
        status: status,
        search: search,
      ),
    );
  }

  @override
  Future<UserProfile> get(String id) => _guard(() => _remoteDataSource.get(id));

  @override
  Future<UserProfile> me() => _guard(_remoteDataSource.me);

  @override
  Future<UserProfile> create(UserCreateInput input) =>
      _guard(() => _remoteDataSource.create(input));

  @override
  Future<UserProfile> update(String id, UserUpdateInput input) =>
      _guard(() => _remoteDataSource.update(id, input));

  @override
  Future<UserProfile> updateMe(ProfileUpdateInput input) =>
      _guard(() => _remoteDataSource.updateMe(input));

  @override
  Future<UserProfile> activate(String id) =>
      _guard(() => _remoteDataSource.activate(id));

  @override
  Future<UserProfile> deactivate(String id) =>
      _guard(() => _remoteDataSource.deactivate(id));

  @override
  Future<UserProfile> block(String id) =>
      _guard(() => _remoteDataSource.block(id));

  @override
  Future<UserProfile> unblock(String id) =>
      _guard(() => _remoteDataSource.unblock(id));

  @override
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) {
    return _guard(
      () => _remoteDataSource.changePassword(
        currentPassword: currentPassword,
        newPassword: newPassword,
      ),
    );
  }

  @override
  Future<void> resetPassword({
    required String id,
    required String temporaryPassword,
  }) {
    return _guard(
      () => _remoteDataSource.resetPassword(
        id: id,
        temporaryPassword: temporaryPassword,
      ),
    );
  }

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }
}

final userRepositoryProvider = Provider<UserRepository>((ref) {
  return UserRepositoryImpl(ref.watch(userRemoteDataSourceProvider));
});
