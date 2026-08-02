import 'warehouse_location.dart';
import 'warehouse_location_input.dart';
import 'warehouse_location_repository.dart';

class ListWarehouseLocationsUseCase {
  const ListWarehouseLocationsUseCase(this.repository);

  final WarehouseLocationRepository repository;

  Future<List<WarehouseLocation>> execute({
    String? warehouseId,
    String? zoneId,
    String? search,
    bool? isActive,
  }) {
    return repository.list(
      warehouseId: warehouseId,
      zoneId: zoneId,
      search: search,
      isActive: isActive,
    );
  }
}

class GetWarehouseLocationUseCase {
  const GetWarehouseLocationUseCase(this.repository);

  final WarehouseLocationRepository repository;

  Future<WarehouseLocation> execute(String id) {
    return repository.get(id);
  }
}

class CreateWarehouseLocationUseCase {
  const CreateWarehouseLocationUseCase(this.repository);

  final WarehouseLocationRepository repository;

  Future<WarehouseLocation> execute(WarehouseLocationInput input) {
    return repository.create(input);
  }
}

class UpdateWarehouseLocationUseCase {
  const UpdateWarehouseLocationUseCase(this.repository);

  final WarehouseLocationRepository repository;

  Future<WarehouseLocation> execute(String id, WarehouseLocationInput input) {
    return repository.update(id, input);
  }
}
