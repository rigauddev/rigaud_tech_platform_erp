import 'warehouse.dart';
import 'warehouse_input.dart';
import 'warehouse_repository.dart';

class ListWarehousesUseCase {
  const ListWarehousesUseCase(this._repository);

  final WarehouseRepository _repository;

  Future<List<Warehouse>> execute({bool? isActive}) {
    return _repository.list(isActive: isActive);
  }
}

class GetWarehouseUseCase {
  const GetWarehouseUseCase(this._repository);

  final WarehouseRepository _repository;

  Future<Warehouse> execute(String id) => _repository.get(id);
}

class CreateWarehouseUseCase {
  const CreateWarehouseUseCase(this._repository);

  final WarehouseRepository _repository;

  Future<Warehouse> execute(WarehouseInput input) => _repository.create(input);
}

class UpdateWarehouseUseCase {
  const UpdateWarehouseUseCase(this._repository);

  final WarehouseRepository _repository;

  Future<Warehouse> execute(String id, WarehouseInput input) {
    return _repository.update(id, input);
  }
}
