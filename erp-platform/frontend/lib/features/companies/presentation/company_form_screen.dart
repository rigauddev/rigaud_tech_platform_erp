import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/company.dart';
import '../domain/company_input.dart';
import 'company_controller.dart';

class CompanyFormScreen extends ConsumerStatefulWidget {
  const CompanyFormScreen({this.companyId, super.key});

  final String? companyId;

  @override
  ConsumerState<CompanyFormScreen> createState() => _CompanyFormScreenState();
}

class _CompanyFormScreenState extends ConsumerState<CompanyFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _legalName = TextEditingController();
  final _tradeName = TextEditingController();
  final _document = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  final _slug = TextEditingController();
  final _code = TextEditingController();
  final _timezone = TextEditingController(text: 'America/Sao_Paulo');
  final _locale = TextEditingController(text: 'pt-BR');
  final _currency = TextEditingController(text: 'BRL');
  bool _hydrated = false;
  bool _saving = false;

  bool get _isEditing => widget.companyId != null;

  @override
  void dispose() {
    _legalName.dispose();
    _tradeName.dispose();
    _document.dispose();
    _email.dispose();
    _phone.dispose();
    _slug.dispose();
    _code.dispose();
    _timezone.dispose();
    _locale.dispose();
    _currency.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final details = _isEditing
        ? ref.watch(companyDetailsProvider(widget.companyId!))
        : null;
    details?.whenData(_hydrate);

    return AppScaffold(
      title: _isEditing ? 'Editar empresa' : 'Nova empresa',
      body:
          details?.when(
            data: (_) => _buildForm(context),
            error: (error, stackTrace) => Center(child: Text(_message(error))),
            loading: () => const Center(child: CircularProgressIndicator()),
          ) ??
          _buildForm(context),
    );
  }

  void _hydrate(Company company) {
    if (_hydrated) {
      return;
    }
    _legalName.text = company.legalName;
    _tradeName.text = company.tradeName;
    _document.text = company.document;
    _email.text = company.email ?? '';
    _phone.text = company.phone ?? '';
    _slug.text = company.slug;
    _code.text = company.code;
    _timezone.text = company.timezone;
    _locale.text = company.locale;
    _currency.text = company.currency;
    _hydrated = true;
  }

  Widget _buildForm(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Form(
        key: _formKey,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth >= 800;
            final fields = [
              _field(_legalName, 'Razão social'),
              _field(_tradeName, 'Nome fantasia'),
              _field(_document, 'CNPJ', validator: _requiredCnpj),
              _field(_email, 'Email', validator: _optionalEmail),
              _field(_phone, 'Telefone'),
              _field(_slug, 'Slug', validator: _requiredSlug),
              _field(_code, 'Código', validator: _requiredCode),
              _field(_timezone, 'Timezone'),
              _field(_locale, 'Locale'),
              _field(_currency, 'Moeda'),
            ];
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Wrap(
                  spacing: AppSpacing.md,
                  runSpacing: AppSpacing.md,
                  children: fields
                      .map(
                        (field) => SizedBox(
                          width: isWide
                              ? (constraints.maxWidth - AppSpacing.md) / 2
                              : double.infinity,
                          child: field,
                        ),
                      )
                      .toList(),
                ),
                const SizedBox(height: AppSpacing.lg),
                Align(
                  alignment: Alignment.centerRight,
                  child: AppButton(
                    label: 'Salvar',
                    icon: Icons.save_outlined,
                    isLoading: _saving,
                    onPressed: _save,
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  TextFormField _field(
    TextEditingController controller,
    String label, {
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
      validator: validator ?? _required,
    );
  }

  String? _required(String? value) {
    return value == null || value.trim().isEmpty ? 'Campo obrigatório' : null;
  }

  String? _requiredCnpj(String? value) {
    final digits = (value ?? '').replaceAll(RegExp(r'\D'), '');
    if (digits.length != 14) {
      return 'CNPJ inválido';
    }
    return null;
  }

  String? _requiredSlug(String? value) {
    final text = value ?? '';
    if (!RegExp(r'^[a-z0-9]+(?:-[a-z0-9]+)*$').hasMatch(text)) {
      return 'Slug inválido';
    }
    return null;
  }

  String? _requiredCode(String? value) {
    final text = value ?? '';
    if (!RegExp(r'^[A-Z0-9][A-Z0-9_-]{1,19}$').hasMatch(text.toUpperCase())) {
      return 'Código inválido';
    }
    return null;
  }

  String? _optionalEmail(String? value) {
    final text = value?.trim() ?? '';
    if (text.isEmpty) {
      return null;
    }
    return RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(text)
        ? null
        : 'Email inválido';
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    setState(() => _saving = true);
    final input = CompanyInput(
      legalName: _legalName.text.trim(),
      tradeName: _tradeName.text.trim(),
      document: _document.text.trim(),
      email: _email.text.trim().isEmpty ? null : _email.text.trim(),
      phone: _phone.text.trim().isEmpty ? null : _phone.text.trim(),
      slug: _slug.text.trim(),
      code: _code.text.trim().toUpperCase(),
      timezone: _timezone.text.trim(),
      locale: _locale.text.trim(),
      currency: _currency.text.trim().toUpperCase(),
    );
    final controller = ref.read(companiesControllerProvider.notifier);
    final company = _isEditing
        ? await controller.updateCompany(widget.companyId!, input)
        : await controller.create(input);
    if (!mounted) {
      return;
    }
    setState(() => _saving = false);
    if (company != null) {
      context.go('${AppRoutes.companies}/${company.id}');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_message(ref.read(companiesControllerProvider).error)),
        ),
      );
    }
  }

  String _message(Object? error) {
    final message = error?.toString() ?? 'Não foi possível salvar a empresa.';
    if (message.contains('409')) {
      return 'Documento, slug ou código já cadastrado.';
    }
    if (message.contains('404')) {
      return 'Empresa não encontrada.';
    }
    return 'Não foi possível salvar a empresa.';
  }
}
