import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/company.dart';
import 'company_controller.dart';

class CompanyDetailScreen extends ConsumerWidget {
  const CompanyDetailScreen({required this.companyId, super.key});

  final String companyId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final company = ref.watch(companyDetailsProvider(companyId));
    return AppScaffold(
      title: 'Empresa',
      body: company.when(
        data: (item) => _CompanyDetail(company: item),
        error: (error, stackTrace) =>
            const Center(child: Text('Empresa não encontrada.')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class CurrentCompanyScreen extends ConsumerWidget {
  const CurrentCompanyScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final company = ref.watch(currentCompanyProvider);
    return AppScaffold(
      title: 'Minha empresa',
      body: company.when(
        data: (item) => _CompanyDetail(company: item, readOnly: true),
        error: (error, stackTrace) =>
            const Center(child: Text('Empresa atual não encontrada.')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _CompanyDetail extends ConsumerWidget {
  const _CompanyDetail({required this.company, this.readOnly = false});

  final Company company;
  final bool readOnly;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            Chip(label: Text(company.status.label)),
            Chip(label: Text(company.currency)),
            Chip(label: Text(company.locale)),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        _row('Razão social', company.legalName),
        _row('Nome fantasia', company.tradeName),
        _row('CNPJ', company.document),
        _row('Email', company.email ?? '-'),
        _row('Telefone', company.phone ?? '-'),
        _row('Slug', company.slug),
        _row('Código', company.code),
        _row('Timezone', company.timezone),
        if (!readOnly) ...[
          const SizedBox(height: AppSpacing.lg),
          Wrap(
            spacing: AppSpacing.sm,
            runSpacing: AppSpacing.sm,
            children: [
              FilledButton.icon(
                icon: const Icon(Icons.edit_outlined),
                label: const Text('Editar'),
                onPressed: () =>
                    context.go('${AppRoutes.companies}/${company.id}/edit'),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.check_circle_outline),
                label: const Text('Ativar'),
                onPressed: () => ref
                    .read(companiesControllerProvider.notifier)
                    .activate(company.id),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.pause_circle_outline),
                label: const Text('Desativar'),
                onPressed: () => ref
                    .read(companiesControllerProvider.notifier)
                    .deactivate(company.id),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.block_outlined),
                label: const Text('Suspender'),
                onPressed: () => ref
                    .read(companiesControllerProvider.notifier)
                    .suspend(company.id),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 4),
          Text(value),
        ],
      ),
    );
  }
}
