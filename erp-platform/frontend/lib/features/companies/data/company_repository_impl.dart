import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../domain/company.dart';
import '../domain/company_input.dart';
import '../domain/company_repository.dart';
import 'company_remote_data_source.dart';

class CompanyRepositoryImpl implements CompanyRepository {
  const CompanyRepositoryImpl(this._remoteDataSource);

  final CompanyRemoteDataSource _remoteDataSource;

  @override
  Future<List<Company>> list() => _guard(_remoteDataSource.list);

  @override
  Future<Company> get(String id) => _guard(() => _remoteDataSource.get(id));

  @override
  Future<Company> current() => _guard(_remoteDataSource.current);

  @override
  Future<Company> create(CompanyInput input) =>
      _guard(() => _remoteDataSource.create(input));

  @override
  Future<Company> update(String id, CompanyInput input) {
    return _guard(() => _remoteDataSource.update(id, input));
  }

  @override
  Future<Company> activate(String id) =>
      _guard(() => _remoteDataSource.activate(id));

  @override
  Future<Company> deactivate(String id) =>
      _guard(() => _remoteDataSource.deactivate(id));

  @override
  Future<Company> suspend(String id) =>
      _guard(() => _remoteDataSource.suspend(id));

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw mapDioError(error);
    }
  }
}

final companyRepositoryProvider = Provider<CompanyRepository>((ref) {
  return CompanyRepositoryImpl(ref.watch(companyRemoteDataSourceProvider));
});
