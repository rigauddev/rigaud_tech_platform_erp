import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/company_repository_impl.dart';
import '../domain/company.dart';
import '../domain/company_input.dart';
import '../domain/company_repository.dart';
import '../domain/company_use_cases.dart';

final companiesControllerProvider =
    AsyncNotifierProvider<CompaniesController, List<Company>>(
      CompaniesController.new,
    );

final companyDetailsProvider = FutureProvider.family<Company, String>((
  ref,
  id,
) {
  return GetCompanyUseCase(ref.watch(companyRepositoryProvider)).execute(id);
});

final currentCompanyProvider = FutureProvider<Company>((ref) {
  return ref.watch(companyRepositoryProvider).current();
});

class CompaniesController extends AsyncNotifier<List<Company>> {
  CompanyRepository get _repository => ref.read(companyRepositoryProvider);

  @override
  Future<List<Company>> build() {
    return ListCompaniesUseCase(_repository).execute();
  }

  Future<void> reload() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ListCompaniesUseCase(_repository).execute(),
    );
  }

  Future<Company?> create(CompanyInput input) async {
    final result = await AsyncValue.guard(
      () => CreateCompanyUseCase(_repository).execute(input),
    );
    if (result.hasValue) {
      await reload();
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<Company?> updateCompany(String id, CompanyInput input) async {
    final result = await AsyncValue.guard(
      () => UpdateCompanyUseCase(_repository).execute(id, input),
    );
    if (result.hasValue) {
      await reload();
      ref.invalidate(companyDetailsProvider(id));
      return result.value;
    }
    state = AsyncError(result.error!, result.stackTrace!);
    return null;
  }

  Future<void> activate(String id) =>
      _changeStatus(() => ActivateCompanyUseCase(_repository).execute(id));

  Future<void> deactivate(String id) {
    return _changeStatus(
      () => DeactivateCompanyUseCase(_repository).execute(id),
    );
  }

  Future<void> suspend(String id) =>
      _changeStatus(() => _repository.suspend(id));

  Future<void> _changeStatus(Future<Company> Function() action) async {
    final result = await AsyncValue.guard(action);
    if (result.hasValue) {
      await reload();
    } else {
      state = AsyncError(result.error!, result.stackTrace!);
    }
  }
}
