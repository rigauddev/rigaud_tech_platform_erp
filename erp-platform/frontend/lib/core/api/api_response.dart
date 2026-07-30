class FieldError {
  const FieldError({
    required this.field,
    required this.code,
    required this.message,
  });

  final String field;
  final String code;
  final String message;

  factory FieldError.fromJson(Map<String, dynamic> json) {
    return FieldError(
      field: json['field'] as String? ?? '',
      code: json['code'] as String? ?? 'INVALID_FIELD',
      message: json['message'] as String? ?? 'Campo inválido.',
    );
  }
}

class PaginationMeta {
  const PaginationMeta({
    required this.page,
    required this.pageSize,
    required this.total,
    required this.totalPages,
  });

  final int page;
  final int pageSize;
  final int total;
  final int totalPages;

  factory PaginationMeta.fromJson(Map<String, dynamic> json) {
    return PaginationMeta(
      page: json['page'] as int? ?? 1,
      pageSize: json['page_size'] as int? ?? 20,
      total: json['total'] as int? ?? 0,
      totalPages: json['total_pages'] as int? ?? 0,
    );
  }
}

class ApiEnvelope {
  const ApiEnvelope({
    required this.success,
    required this.code,
    required this.message,
    this.data,
    this.meta,
    this.errors,
    this.requestId,
  });

  final bool success;
  final String code;
  final String message;
  final dynamic data;
  final PaginationMeta? meta;
  final List<FieldError>? errors;
  final String? requestId;

  factory ApiEnvelope.fromJson(Map<String, dynamic> json) {
    final errors = json['errors'] as List<dynamic>?;
    final meta = json['meta'] as Map<String, dynamic>?;
    return ApiEnvelope(
      success: json['success'] as bool? ?? true,
      code: json['code'] as String? ?? 'API_SUCCESS',
      message: json['message'] as String? ?? 'Operação concluída.',
      data: json.containsKey('data') ? json['data'] : json,
      meta: meta == null ? null : PaginationMeta.fromJson(meta),
      errors: errors
          ?.map((error) => FieldError.fromJson(error as Map<String, dynamic>))
          .toList(),
      requestId: json['request_id'] as String?,
    );
  }
}

Map<String, dynamic> apiDataObject(Map<String, dynamic>? json) {
  final envelope = ApiEnvelope.fromJson(json ?? {});
  final data = envelope.data;
  if (data is Map<String, dynamic>) {
    return data;
  }
  return {};
}

List<dynamic> apiDataList(Map<String, dynamic>? json) {
  final envelope = ApiEnvelope.fromJson(json ?? {});
  final data = envelope.data;
  if (data is List<dynamic>) {
    return data;
  }
  return [];
}
