import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/presentation/auth_controller.dart';
import 'app_routes.dart';

final authGuardEnabledProvider = Provider<bool>((ref) {
  return true;
});

final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(authControllerProvider).value?.isAuthenticated ?? false;
});

final isSuperuserProvider = Provider<bool>((ref) {
  return ref.watch(authControllerProvider).value?.user?.isSuperuser ?? false;
});

class RouteGuard {
  const RouteGuard({
    required this.enabled,
    required this.isAuthenticated,
    required this.isSuperuser,
  });

  final bool enabled;
  final bool isAuthenticated;
  final bool isSuperuser;

  String? redirect(String location) {
    if (!enabled) {
      return null;
    }

    final isProtectedRoute =
        location == AppRoutes.dashboard ||
        location.startsWith('${AppRoutes.dashboard}/') ||
        location.startsWith(AppRoutes.categories) ||
        location.startsWith(AppRoutes.inventory) ||
        location.startsWith(AppRoutes.warehouses) ||
        location.startsWith(AppRoutes.warehouseZones) ||
        location.startsWith(AppRoutes.warehouseLocations) ||
        location.startsWith(AppRoutes.companies) ||
        location.startsWith(AppRoutes.users) ||
        location.startsWith(AppRoutes.audit);
    if (!isAuthenticated && isProtectedRoute) {
      return AppRoutes.login;
    }
    final isCompanyAdminRoute =
        location == AppRoutes.companies ||
        location == AppRoutes.companyCreate ||
        (location.startsWith('${AppRoutes.companies}/') &&
            location != AppRoutes.currentCompany);
    if (isAuthenticated && isCompanyAdminRoute && !isSuperuser) {
      return AppRoutes.currentCompany;
    }
    final isUserAdminRoute =
        location == AppRoutes.users ||
        location == AppRoutes.userCreate ||
        (location.startsWith('${AppRoutes.users}/') &&
            location != AppRoutes.currentUser &&
            location != AppRoutes.changeMyPassword &&
            location != AppRoutes.mfaSettings);
    if (isAuthenticated && isUserAdminRoute && !isSuperuser) {
      return AppRoutes.currentUser;
    }
    if (isAuthenticated &&
        location.startsWith(AppRoutes.audit) &&
        !isSuperuser) {
      return AppRoutes.currentUser;
    }
    if (isAuthenticated && location == AppRoutes.login) {
      return AppRoutes.dashboard;
    }
    return null;
  }
}
