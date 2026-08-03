import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/receiving_document.dart';
import '../domain/receiving_document_input.dart';
import '../domain/receiving_document_repository.dart';
import 'receiving_document_remote_data_source.dart';

class ReceivingDocumentRepositoryImpl implements ReceivingDocumentRepository {
  const ReceivingDocumentRepositoryImpl(this._remote);

  final ReceivingDocumentRemoteDataSource _remote;

  @override
  Future<List<ReceivingDocument>> list({
    String? warehouseId,
    ReceivingDocumentStatus? status,
    String? search,
    int page = 1,
    int pageSize = 20,
  }) {
    return _remote.list(
      warehouseId: warehouseId,
      status: status,
      search: search,
      page: page,
      pageSize: pageSize,
    );
  }

  @override
  Future<ReceivingDocument> get(String id) {
    return _remote.get(id);
  }

  @override
  Future<ReceivingDocument> create(ReceivingDocumentInput input) {
    return _remote.create(input);
  }

  @override
  Future<ReceivingDocument> update(String id, ReceivingDocumentInput input) {
    return _remote.update(id, input);
  }

  @override
  Future<ReceivingDocument> changeStatus(
    String id,
    ReceivingStatusInput input,
  ) {
    return _remote.changeStatus(id, input);
  }

  @override
  Future<ReceivingDocument> confirmReceipt(String id, {String? notes}) {
    return _remote.confirmReceipt(id, notes: notes);
  }

  @override
  Future<ReceivingDocument> delete(String id) {
    return _remote.delete(id);
  }
}

final receivingDocumentRepositoryProvider =
    Provider<ReceivingDocumentRepository>((ref) {
      return ReceivingDocumentRepositoryImpl(
        ref.watch(receivingDocumentRemoteDataSourceProvider),
      );
    });
