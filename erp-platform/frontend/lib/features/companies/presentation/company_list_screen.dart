import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_empty_state.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/company.dart';
import 'company_controller.dart';

class CompanyListScreen extends ConsumerWidget {
  const CompanyListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final companies = ref.watch(companiesControllerProvider);
    return AppScaffold(
      title: 'Empresas',
      actions: [
        IconButton(
          tooltip: 'Nova empresa',
          icon: const Icon(Icons.add_business_outlined),
          onPressed: () => context.go(AppRoutes.companyCreate),
        ),
      ],
      body: companies.when(
        data: (items) {
          if (items.isEmpty) {
            return const AppEmptyState(
              title: 'Nenhuma empresa cadastrada',
              message:
                  'Crie a primeira empresa para iniciar a gestão de tenants.',
            );
          }
          return LayoutBuilder(
            builder: (context, constraints) {
              if (constraints.maxWidth >= 900) {
                return _CompanyTable(items: items);
              }
              return _CompanyCards(items: items);
            },
          );
        },
        error: (error, stackTrace) => Center(child: Text(_message(error))),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  String _message(Object error) {
    final text = error.toString();
    if (text.contains('403')) {
      return 'Acesso restrito a superusuários.';
    }
    return 'Não foi possível carregar empresas.';
  }
}

class _CompanyTable extends StatelessWidget {
  const _CompanyTable({required this.items});

  final List<Company> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Nome fantasia')),
          DataColumn(label: Text('CNPJ')),
          DataColumn(label: Text('Slug')),
          DataColumn(label: Text('Código')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Ações')),
        ],
        rows: items
            .map(
              (company) => DataRow(
                cells: [
                  DataCell(Text(company.tradeName)),
                  DataCell(Text(company.document)),
                  DataCell(Text(company.slug)),
                  DataCell(Text(company.code)),
                  DataCell(Text(company.status.label)),
                  DataCell(
                    IconButton(
                      tooltip: 'Detalhes',
                      icon: const Icon(Icons.open_in_new),
                      onPressed: () =>
                          context.go('${AppRoutes.companies}/${company.id}'),
                    ),
                  ),
                ],
              ),
            )
            .toList(),
      ),
    );
  }
}

class _CompanyCards extends StatelessWidget {
  const _CompanyCards({required this.items});

  final List<Company> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final company = items[index];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.business_outlined),
            title: Text(company.tradeName),
            subtitle: Text('${company.code} · ${company.status.label}'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go('${AppRoutes.companies}/${company.id}'),
          ),
        );
      },
    );
  }
}
