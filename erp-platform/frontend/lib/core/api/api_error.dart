import '../errors/app_error.dart';

class ApiError extends AppError {
  const ApiError(super.message, {super.code, this.statusCode, this.requestId});

  final int? statusCode;
  final String? requestId;
}
