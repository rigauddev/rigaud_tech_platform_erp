import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/company.dart';
import '../domain/company_input.dart';

class CompanyRemoteDataSource {
  const CompanyRemoteDataSource(this._dio);

  final Dio _dio;

  Future<List<Company>> list() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/companies');
    final items = apiDataList(response.data);
    return items
        .map((item) => Company.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Company> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/companies/$id',
    );
    return Company.fromJson(apiDataObject(response.data));
  }

  Future<Company> current() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/companies/current',
    );
    return Company.fromJson(apiDataObject(response.data));
  }

  Future<Company> create(CompanyInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/companies',
      data: input.toJson(),
    );
    return Company.fromJson(apiDataObject(response.data));
  }

  Future<Company> update(String id, CompanyInput input) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/api/v1/companies/$id',
      data: input.toJson(),
    );
    return Company.fromJson(apiDataObject(response.data));
  }

  Future<Company> activate(String id) => _statusAction(id, 'activate');

  Future<Company> deactivate(String id) => _statusAction(id, 'deactivate');

  Future<Company> suspend(String id) => _statusAction(id, 'suspend');

  Future<Company> _statusAction(String id, String action) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/companies/$id/$action',
    );
    return Company.fromJson(apiDataObject(response.data));
  }
}

final companyRemoteDataSourceProvider = Provider<CompanyRemoteDataSource>((
  ref,
) {
  return CompanyRemoteDataSource(ref.watch(dioProvider));
});
