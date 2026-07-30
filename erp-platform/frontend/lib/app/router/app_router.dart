import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/mfa/presentation/mfa_settings_screen.dart';
import '../../features/auth/mfa/presentation/mfa_verify_screen.dart';
import '../../features/audit/presentation/audit_detail_screen.dart';
import '../../features/audit/presentation/audit_list_screen.dart';
import '../../features/companies/presentation/company_detail_screen.dart';
import '../../features/companies/presentation/company_form_screen.dart';
import '../../features/companies/presentation/company_list_screen.dart';
import '../../features/dashboard/presentation/dashboard_screen.dart';
import '../../features/not_found/presentation/not_found_screen.dart';
import '../../features/splash/presentation/splash_screen.dart';
import '../../features/users/presentation/user_detail_screen.dart';
import '../../features/users/presentation/user_form_screen.dart';
import '../../features/users/presentation/user_list_screen.dart';
import '../../features/users/presentation/user_password_screens.dart';
import 'app_routes.dart';
import 'route_guard.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final guard = RouteGuard(
    enabled: ref.watch(authGuardEnabledProvider),
    isAuthenticated: ref.watch(isAuthenticatedProvider),
    isSuperuser: ref.watch(isSuperuserProvider),
  );

  return GoRouter(
    initialLocation: AppRoutes.splash,
    redirect: (context, state) => guard.redirect(state.uri.path),
    errorBuilder: (context, state) => const NotFoundScreen(),
    routes: [
      GoRoute(
        path: AppRoutes.splash,
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: AppRoutes.mfaVerify,
        builder: (context, state) => const MfaVerifyScreen(),
      ),
      GoRoute(
        path: AppRoutes.dashboard,
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: AppRoutes.companies,
        builder: (context, state) => const CompanyListScreen(),
      ),
      GoRoute(
        path: AppRoutes.companyCreate,
        builder: (context, state) => const CompanyFormScreen(),
      ),
      GoRoute(
        path: AppRoutes.currentCompany,
        builder: (context, state) => const CurrentCompanyScreen(),
      ),
      GoRoute(
        path: '${AppRoutes.companies}/:companyId',
        builder: (context, state) => CompanyDetailScreen(
          companyId: state.pathParameters['companyId'] ?? '',
        ),
      ),
      GoRoute(
        path: '${AppRoutes.companies}/:companyId/edit',
        builder: (context, state) =>
            CompanyFormScreen(companyId: state.pathParameters['companyId']),
      ),
      GoRoute(
        path: AppRoutes.users,
        builder: (context, state) => const UserListScreen(),
      ),
      GoRoute(
        path: AppRoutes.userCreate,
        builder: (context, state) => const UserFormScreen(),
      ),
      GoRoute(
        path: AppRoutes.currentUser,
        builder: (context, state) => const CurrentUserProfileScreen(),
      ),
      GoRoute(
        path: AppRoutes.changeMyPassword,
        builder: (context, state) => const ChangeMyPasswordScreen(),
      ),
      GoRoute(
        path: AppRoutes.mfaSettings,
        builder: (context, state) => const MfaSettingsScreen(),
      ),
      GoRoute(
        path: '${AppRoutes.users}/:userId',
        builder: (context, state) =>
            UserDetailScreen(userId: state.pathParameters['userId'] ?? ''),
      ),
      GoRoute(
        path: '${AppRoutes.users}/:userId/edit',
        builder: (context, state) =>
            UserFormScreen(userId: state.pathParameters['userId']),
      ),
      GoRoute(
        path: '${AppRoutes.users}/:userId/reset-password',
        builder: (context, state) => ResetUserPasswordScreen(
          userId: state.pathParameters['userId'] ?? '',
        ),
      ),
      GoRoute(
        path: AppRoutes.audit,
        builder: (context, state) => const AuditListScreen(),
      ),
      GoRoute(
        path: '${AppRoutes.audit}/:eventId',
        builder: (context, state) =>
            AuditDetailScreen(eventId: state.pathParameters['eventId'] ?? ''),
      ),
      GoRoute(
        path: AppRoutes.notFound,
        builder: (context, state) => const NotFoundScreen(),
      ),
    ],
  );
});
