class AppRoutes {
  const AppRoutes._();

  static const splash = '/';
  static const login = '/login';
  static const mfaVerify = '/login/mfa';
  static const dashboard = '/dashboard';
  static const companies = '/companies';
  static const companyCreate = '/companies/new';
  static const currentCompany = '/companies/current';
  static const users = '/users';
  static const userCreate = '/users/new';
  static const currentUser = '/users/me';
  static const changeMyPassword = '/users/me/change-password';
  static const mfaSettings = '/users/me/mfa';
  static const products = '/products';
  static const productCreate = '/products/new';
  static const categories = '/categories';
  static const categoryCreate = '/categories/new';
  static const inventory = '/inventory';
  static const warehouses = '/warehouses';
  static const warehouseCreate = '/warehouses/new';
  static const warehouseZones = '/warehouse-zones';
  static const warehouseZoneCreate = '/warehouse-zones/new';
  static const warehouseLocations = '/warehouse-locations';
  static const warehouseLocationCreate = '/warehouse-locations/new';
  static const audit = '/audit';
  static const demo = '/demo';
  static const notFound = '/not-found';
}
