import 'company.dart';
import 'company_input.dart';

abstract interface class CompanyRepository {
  Future<List<Company>> list();

  Future<Company> get(String id);

  Future<Company> current();

  Future<Company> create(CompanyInput input);

  Future<Company> update(String id, CompanyInput input);

  Future<Company> activate(String id);

  Future<Company> deactivate(String id);

  Future<Company> suspend(String id);
}
