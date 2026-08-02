import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/features/receiving_documents/data/receiving_document_repository_impl.dart';
import 'package:rigaud_tech_erp/features/receiving_documents/domain/receiving_document.dart';
import 'package:rigaud_tech_erp/features/receiving_documents/domain/receiving_document_input.dart';
import 'package:rigaud_tech_erp/features/receiving_documents/domain/receiving_document_repository.dart';
import 'package:rigaud_tech_erp/features/receiving_documents/presentation/receiving_document_controller.dart';

void main() {
  test('ReceivingDocumentsController lista, cria e muda status', () async {
    final repository = _FakeReceivingDocumentRepository();
    final container = ProviderContainer(
      overrides: [
        receivingDocumentRepositoryProvider.overrideWithValue(repository),
      ],
    );
    addTearDown(container.dispose);

    final initial = await container.read(
      receivingDocumentsControllerProvider.future,
    );
    expect(initial, isEmpty);

    final created = await container
        .read(receivingDocumentsControllerProvider.notifier)
        .create(
          const ReceivingDocumentInput(
            warehouseId: 'warehouse-1',
            documentNumber: 'NF-001',
            documentType: 'invoice',
            status: ReceivingDocumentStatus.expected,
            items: [
              ReceivingItemInput(
                productId: 'product-1',
                orderedQuantity: 10,
                receivedQuantity: 2,
                damagedQuantity: 1,
                unitCost: 15,
              ),
            ],
          ),
        );

    expect(created?.documentNumber, 'NF-001');
    expect(created?.pendingTotal, 7);
    expect(
      container.read(receivingDocumentsControllerProvider).value,
      hasLength(1),
    );

    await container
        .read(receivingDocumentsControllerProvider.notifier)
        .changeStatus(created!.id, ReceivingDocumentStatus.receiving);

    expect(repository._items.single.status, ReceivingDocumentStatus.receiving);
  });
}

class _FakeReceivingDocumentRepository implements ReceivingDocumentRepository {
  final List<ReceivingDocument> _items = [];

  @override
  Future<List<ReceivingDocument>> list({
    String? warehouseId,
    ReceivingDocumentStatus? status,
    String? search,
    int page = 1,
    int pageSize = 20,
  }) async {
    return _items
        .where((item) => warehouseId == null || item.warehouseId == warehouseId)
        .where((item) => status == null || item.status == status)
        .where(
          (item) =>
              search == null ||
              item.documentNumber.toLowerCase().contains(search.toLowerCase()),
        )
        .toList();
  }

  @override
  Future<ReceivingDocument> get(String id) async {
    return _items.firstWhere((item) => item.id == id);
  }

  @override
  Future<ReceivingDocument> create(ReceivingDocumentInput input) async {
    final document = _build(input, id: 'receiving-${_items.length + 1}');
    _items.add(document);
    return document;
  }

  @override
  Future<ReceivingDocument> update(
    String id,
    ReceivingDocumentInput input,
  ) async {
    final index = _items.indexWhere((item) => item.id == id);
    final updated = _build(input, id: id);
    _items[index] = updated;
    return updated;
  }

  @override
  Future<ReceivingDocument> changeStatus(
    String id,
    ReceivingStatusInput input,
  ) async {
    final current = await get(id);
    final updated = _copy(current, status: input.status);
    _items[_items.indexWhere((item) => item.id == id)] = updated;
    return updated;
  }

  @override
  Future<ReceivingDocument> delete(String id) async {
    return changeStatus(
      id,
      const ReceivingStatusInput(status: ReceivingDocumentStatus.cancelled),
    );
  }

  ReceivingDocument _build(ReceivingDocumentInput input, {required String id}) {
    final items = input.items
        .map(
          (item) => ReceivingItem(
            id: 'item-${input.items.indexOf(item) + 1}',
            tenantId: 'tenant-1',
            documentId: id,
            productId: item.productId,
            orderedQuantity: item.orderedQuantity,
            receivedQuantity: item.receivedQuantity,
            damagedQuantity: item.damagedQuantity,
            pendingQuantity:
                item.orderedQuantity -
                item.receivedQuantity -
                item.damagedQuantity,
            unitCost: item.unitCost,
          ),
        )
        .toList();
    return ReceivingDocument(
      id: id,
      tenantId: 'tenant-1',
      branchId: 'branch-1',
      warehouseId: input.warehouseId,
      supplierId: input.supplierId,
      documentNumber: input.documentNumber,
      documentType: input.documentType,
      status: input.status,
      expectedDate: input.expectedDate,
      receivedDate: input.receivedDate,
      notes: input.notes,
      items: items,
      createdAt: DateTime.utc(2026, 8, 2),
      updatedAt: DateTime.utc(2026, 8, 2),
    );
  }

  ReceivingDocument _copy(
    ReceivingDocument document, {
    ReceivingDocumentStatus? status,
  }) {
    return ReceivingDocument(
      id: document.id,
      tenantId: document.tenantId,
      branchId: document.branchId,
      warehouseId: document.warehouseId,
      supplierId: document.supplierId,
      documentNumber: document.documentNumber,
      documentType: document.documentType,
      status: status ?? document.status,
      expectedDate: document.expectedDate,
      receivedDate: document.receivedDate,
      notes: document.notes,
      items: document.items,
      createdAt: document.createdAt,
      updatedAt: DateTime.utc(2026, 8, 2),
    );
  }
}
