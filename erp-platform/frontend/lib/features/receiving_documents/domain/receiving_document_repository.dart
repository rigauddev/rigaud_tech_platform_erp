import 'receiving_document.dart';
import 'receiving_document_input.dart';

abstract interface class ReceivingDocumentRepository {
  Future<List<ReceivingDocument>> list({
    String? warehouseId,
    ReceivingDocumentStatus? status,
    String? search,
    int page = 1,
    int pageSize = 20,
  });

  Future<ReceivingDocument> get(String id);

  Future<ReceivingDocument> create(ReceivingDocumentInput input);

  Future<ReceivingDocument> update(String id, ReceivingDocumentInput input);

  Future<ReceivingDocument> changeStatus(String id, ReceivingStatusInput input);

  Future<ReceivingDocument> delete(String id);
}
