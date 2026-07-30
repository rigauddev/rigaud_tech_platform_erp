import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/audit_repository_impl.dart';
import '../domain/audit_event.dart';
import '../domain/audit_repository.dart';

final auditControllerProvider =
    AsyncNotifierProvider<AuditController, AuditEventPage>(AuditController.new);

final auditEventProvider = FutureProvider.family<AuditEvent, String>((ref, id) {
  return ref.watch(auditRepositoryProvider).get(id);
});

class AuditController extends AsyncNotifier<AuditEventPage> {
  AuditRepository get _repository => ref.read(auditRepositoryProvider);

  String? _module;
  String? _requestId;

  @override
  Future<AuditEventPage> build() => _repository.list();

  Future<void> reload({String? module, String? requestId}) async {
    _module = module ?? _module;
    _requestId = requestId ?? _requestId;
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => _repository.list(module: _module, requestId: _requestId),
    );
  }
}
