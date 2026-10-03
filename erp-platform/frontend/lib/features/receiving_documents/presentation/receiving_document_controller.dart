import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/receiving_document_repository_impl.dart';
import '../domain/receiving_document.dart';
import '../domain/receiving_document_input.dart';
import '../domain/receiving_document_repository.dart';
import '../domain/receiving_document_use_cases.dart';

final receivingDocumentsControllerProvider =
    AsyncNotifierProvider<
      ReceivingDocumentsController,
      List<ReceivingDocument>
    >(ReceivingDocumentsController.new);

final receivingDocumentDetailsProvider =
    FutureProvider.family<ReceivingDocument, String>((ref, id) {
      return GetReceivingDocumentUseCase(
        ref.watch(receivingDocumentRepositoryProvider),
      ).execute(id);
    });

class ReceivingDocumentsController
    extends AsyncNotifier<List<ReceivingDocument>> {
  ReceivingDocumentRepository get _repository =>
      ref.read(receivingDocumentRepositoryProvider);

  @override
  Future<List<ReceivingDocument>> build() {
    return ListReceivingDocumentsUseCase(_repository).execute();
  }

  Future<void> reload({
    String? warehouseId,
    ReceivingDocumentStatus? status,
    String? search,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListReceivingDocumentsUseCase(
        _repository,
      ).execute(warehouseId: warehouseId, status: status, search: search),
    );
  }

  Future<ReceivingDocument?> create(ReceivingDocumentInput input) async {
    final result = await AsyncValue.guard(
      () => CreateReceivingDocumentUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<ReceivingDocument?> updateDocument(
    String id,
    ReceivingDocumentInput input,
  ) async {
    final result = await AsyncValue.guard(
      () => UpdateReceivingDocumentUseCase(_repository).execute(id, input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(receivingDocumentDetailsProvider(id));
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<void> changeStatus(String id, ReceivingDocumentStatus status) {
    return _change(
      id,
      () => _repository.changeStatus(id, ReceivingStatusInput(status: status)),
    );
  }

  Future<void> confirmReceipt(String id, {String? notes}) {
    return _change(id, () => _repository.confirmReceipt(id, notes: notes));
  }

  Future<void> deleteDocument(String id) {
    return _change(id, () => _repository.delete(id));
  }

  Future<void> _change(
    String id,
    Future<ReceivingDocument> Function() action,
  ) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
      ref.invalidate(receivingDocumentDetailsProvider(id));
    } else {
      state = AsyncError(result.error!, result.stackTrace!);
    }
  }
}
