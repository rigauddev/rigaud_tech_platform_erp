import 'company.dart';
import 'company_input.dart';
import 'company_repository.dart';

class ListCompaniesUseCase {
  const ListCompaniesUseCase(this._repository);

  final CompanyRepository _repository;

  Future<List<Company>> execute() => _repository.list();
}

class GetCompanyUseCase {
  const GetCompanyUseCase(this._repository);

  final CompanyRepository _repository;

  Future<Company> execute(String id) => _repository.get(id);
}

class CreateCompanyUseCase {
  const CreateCompanyUseCase(this._repository);

  final CompanyRepository _repository;

  Future<Company> execute(CompanyInput input) => _repository.create(input);
}

class UpdateCompanyUseCase {
  const UpdateCompanyUseCase(this._repository);

  final CompanyRepository _repository;

  Future<Company> execute(String id, CompanyInput input) =>
      _repository.update(id, input);
}

class ActivateCompanyUseCase {
  const ActivateCompanyUseCase(this._repository);

  final CompanyRepository _repository;

  Future<Company> execute(String id) => _repository.activate(id);
}

class DeactivateCompanyUseCase {
  const DeactivateCompanyUseCase(this._repository);

  final CompanyRepository _repository;

  Future<Company> execute(String id) => _repository.deactivate(id);
}
