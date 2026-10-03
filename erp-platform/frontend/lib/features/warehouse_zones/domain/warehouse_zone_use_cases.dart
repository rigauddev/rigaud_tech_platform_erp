import 'warehouse_zone.dart';
import 'warehouse_zone_input.dart';
import 'warehouse_zone_repository.dart';

class ListWarehouseZonesUseCase {
  const ListWarehouseZonesUseCase(this.repository);

  final WarehouseZoneRepository repository;

  Future<List<WarehouseZone>> execute({String? warehouseId, bool? isActive}) {
    return repository.list(warehouseId: warehouseId, isActive: isActive);
  }
}

class GetWarehouseZoneUseCase {
  const GetWarehouseZoneUseCase(this.repository);

  final WarehouseZoneRepository repository;

  Future<WarehouseZone> execute(String id) => repository.get(id);
}

class CreateWarehouseZoneUseCase {
  const CreateWarehouseZoneUseCase(this.repository);

  final WarehouseZoneRepository repository;

  Future<WarehouseZone> execute(WarehouseZoneInput input) {
    return repository.create(input);
  }
}

class UpdateWarehouseZoneUseCase {
  const UpdateWarehouseZoneUseCase(this.repository);

  final WarehouseZoneRepository repository;

  Future<WarehouseZone> execute(String id, WarehouseZoneInput input) {
    return repository.update(id, input);
  }
}
