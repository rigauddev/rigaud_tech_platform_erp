import 'receiving_document.dart';
import 'receiving_document_input.dart';
import 'receiving_document_repository.dart';

class ListReceivingDocumentsUseCase {
  const ListReceivingDocumentsUseCase(this._repository);

  final ReceivingDocumentRepository _repository;

  Future<List<ReceivingDocument>> execute({
    String? warehouseId,
    ReceivingDocumentStatus? status,
    String? search,
  }) {
    return _repository.list(
      warehouseId: warehouseId,
      status: status,
      search: search,
    );
  }
}

class GetReceivingDocumentUseCase {
  const GetReceivingDocumentUseCase(this._repository);

  final ReceivingDocumentRepository _repository;

  Future<ReceivingDocument> execute(String id) {
    return _repository.get(id);
  }
}

class CreateReceivingDocumentUseCase {
  const CreateReceivingDocumentUseCase(this._repository);

  final ReceivingDocumentRepository _repository;

  Future<ReceivingDocument> execute(ReceivingDocumentInput input) {
    return _repository.create(input);
  }
}

class UpdateReceivingDocumentUseCase {
  const UpdateReceivingDocumentUseCase(this._repository);

  final ReceivingDocumentRepository _repository;

  Future<ReceivingDocument> execute(String id, ReceivingDocumentInput input) {
    return _repository.update(id, input);
  }
}
