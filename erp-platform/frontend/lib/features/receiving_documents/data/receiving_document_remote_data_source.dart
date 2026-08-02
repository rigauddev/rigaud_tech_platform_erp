import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_response.dart';
import '../domain/receiving_document.dart';
import '../domain/receiving_document_input.dart';

class ReceivingDocumentRemoteDataSource {
  const ReceivingDocumentRemoteDataSource(this._dio);

  final Dio _dio;

  Future<List<ReceivingDocument>> list({
    String? warehouseId,
    ReceivingDocumentStatus? status,
    String? search,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/receiving-documents',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (warehouseId case final String id) 'warehouse_id': id,
        if (status case final ReceivingDocumentStatus value)
          'status': value.name,
        if (search case final String value) 'search': value,
      },
    );
    return apiDataList(response.data)
        .map((item) => ReceivingDocument.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<ReceivingDocument> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/receiving-documents/$id',
    );
    return ReceivingDocument.fromJson(apiDataObject(response.data));
  }

  Future<ReceivingDocument> create(ReceivingDocumentInput input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/receiving-documents',
      data: input.toJson(),
    );
    return ReceivingDocument.fromJson(apiDataObject(response.data));
  }

  Future<ReceivingDocument> update(
    String id,
    ReceivingDocumentInput input,
  ) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/api/v1/receiving-documents/$id',
      data: input.toJson(),
    );
    return ReceivingDocument.fromJson(apiDataObject(response.data));
  }

  Future<ReceivingDocument> changeStatus(
    String id,
    ReceivingStatusInput input,
  ) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/receiving-documents/$id/status',
      data: input.toJson(),
    );
    return ReceivingDocument.fromJson(apiDataObject(response.data));
  }

  Future<ReceivingDocument> delete(String id) async {
    final response = await _dio.delete<Map<String, dynamic>>(
      '/api/v1/receiving-documents/$id',
    );
    return ReceivingDocument.fromJson(apiDataObject(response.data));
  }
}

final receivingDocumentRemoteDataSourceProvider =
    Provider<ReceivingDocumentRemoteDataSource>((ref) {
      return ReceivingDocumentRemoteDataSource(ref.watch(dioProvider));
    });
