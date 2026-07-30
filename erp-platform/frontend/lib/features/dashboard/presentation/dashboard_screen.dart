import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_spacing.dart';
import '../../auth/presentation/auth_controller.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return AppScaffold(
      title: 'Dashboard',
      actions: [
        IconButton(
          tooltip: 'Sair',
          icon: const Icon(Icons.logout),
          onPressed: () => ref.read(authControllerProvider.notifier).logout(),
        ),
      ],
      body: const Padding(
        padding: EdgeInsets.all(AppSpacing.lg),
        child: AppEmptyState(
          title: 'Dashboard preparado',
          message: 'Os indicadores do ERP serão conectados em uma task futura.',
        ),
      ),
    );
  }
}
