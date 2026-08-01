import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/components/app_error_view.dart';
import '../../../shared/components/app_loading.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/demo_status.dart';
import 'demo_controller.dart';

class DemoDashboardScreen extends ConsumerWidget {
  const DemoDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(demoControllerProvider);

    return AppScaffold(
      title: 'Demo',
      selectedIndex: 8,
      body: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: state.when(
          loading: () => const AppLoading(),
          error: (error, stackTrace) => AppErrorView(
            message: demoErrorMessage(error),
            onRetry: () => ref.read(demoControllerProvider.notifier).refresh(),
          ),
          data: (status) {
            if (status == null) {
              return const AppEmptyState(
                title: 'Demo indisponível',
                message: 'O ambiente demo não retornou status.',
              );
            }
            return _DemoDashboard(status: status);
          },
        ),
      ),
    );
  }
}

class _DemoDashboard extends ConsumerWidget {
  const _DemoDashboard({required this.status});

  final DemoStatus status;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controller = ref.read(demoControllerProvider.notifier);

    return ListView(
      children: [
        Wrap(
          spacing: AppSpacing.md,
          runSpacing: AppSpacing.md,
          children: [
            _MetricCard(label: 'Empresas', value: status.companies),
            _MetricCard(label: 'Filiais', value: status.branches),
            _MetricCard(label: 'Usuários', value: status.users),
            _MetricCard(label: 'Categorias', value: status.categories),
            _MetricCard(label: 'Produtos', value: status.products),
          ],
        ),
        const SizedBox(height: AppSpacing.xl),
        Wrap(
          spacing: AppSpacing.md,
          runSpacing: AppSpacing.md,
          children: [
            FilledButton.icon(
              onPressed: controller.install,
              icon: const Icon(Icons.download_done_outlined),
              label: const Text('Instalar'),
            ),
            OutlinedButton.icon(
              onPressed: controller.refresh,
              icon: const Icon(Icons.refresh),
              label: const Text('Atualizar'),
            ),
            OutlinedButton.icon(
              onPressed: controller.reset,
              icon: const Icon(Icons.restart_alt),
              label: const Text('Reset'),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.xl),
        const AppEmptyState(
          title: 'Cenários planejados',
          message:
              'Mesas, pedidos, estoque, delivery, caixa e vendas serão materializados quando os módulos existirem.',
        ),
      ],
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({required this.label, required this.value});

  final String label;
  final int value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 180,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: AppSpacing.sm),
              Text('$value', style: Theme.of(context).textTheme.headlineMedium),
            ],
          ),
        ),
      ),
    );
  }
}
