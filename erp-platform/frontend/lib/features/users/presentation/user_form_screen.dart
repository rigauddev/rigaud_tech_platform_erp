import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../domain/user.dart';
import '../domain/user_input.dart';
import 'user_controller.dart';

class UserFormScreen extends ConsumerStatefulWidget {
  const UserFormScreen({this.userId, super.key});

  final String? userId;

  @override
  ConsumerState<UserFormScreen> createState() => _UserFormScreenState();
}

class _UserFormScreenState extends ConsumerState<UserFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _tenantId = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _firstName = TextEditingController();
  final _lastName = TextEditingController();
  final _displayName = TextEditingController();
  final _phone = TextEditingController();
  bool _mustChangePassword = true;
  UserStatus _status = UserStatus.active;
  bool _hydrated = false;
  bool _saving = false;

  bool get _isEditing => widget.userId != null;

  @override
  void dispose() {
    _tenantId.dispose();
    _email.dispose();
    _password.dispose();
    _firstName.dispose();
    _lastName.dispose();
    _displayName.dispose();
    _phone.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final details = _isEditing
        ? ref.watch(userDetailsProvider(widget.userId!))
        : null;
    details?.whenData(_hydrate);

    return AppScaffold(
      title: _isEditing ? 'Editar usuário' : 'Novo usuário',
      selectedIndex: 2,
      body:
          details?.when(
            data: (_) => _buildForm(context),
            error: (error, stackTrace) =>
                const Center(child: Text('Usuário não encontrado.')),
            loading: () => const Center(child: CircularProgressIndicator()),
          ) ??
          _buildForm(context),
    );
  }

  void _hydrate(UserProfile user) {
    if (_hydrated) {
      return;
    }
    _tenantId.text = user.tenantId;
    _email.text = user.email;
    _firstName.text = user.firstName ?? '';
    _lastName.text = user.lastName ?? '';
    _displayName.text = user.displayName ?? '';
    _phone.text = user.phone ?? '';
    _mustChangePassword = user.mustChangePassword;
    _status = user.status;
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
              _field(_tenantId, 'Empresa ID', enabled: !_isEditing),
              _field(_email, 'Email', validator: _emailValidator),
              if (!_isEditing)
                _field(_password, 'Senha temporária', obscure: true),
              _field(_firstName, 'Nome'),
              _field(_lastName, 'Sobrenome'),
              _field(_displayName, 'Nome de exibição', required: false),
              _field(_phone, 'Telefone', required: false),
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
                const SizedBox(height: AppSpacing.md),
                DropdownButtonFormField<UserStatus>(
                  initialValue: _status,
                  decoration: const InputDecoration(labelText: 'Status'),
                  items: UserStatus.values
                      .map(
                        (status) => DropdownMenuItem(
                          value: status,
                          child: Text(status.label),
                        ),
                      )
                      .toList(),
                  onChanged: _isEditing
                      ? (value) => setState(() => _status = value!)
                      : null,
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  value: _mustChangePassword,
                  title: const Text('Exigir troca de senha'),
                  onChanged: (value) =>
                      setState(() => _mustChangePassword = value),
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
    bool enabled = true,
    bool obscure = false,
    bool required = true,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      enabled: enabled,
      obscureText: obscure,
      decoration: InputDecoration(labelText: label),
      validator: validator ?? (required ? _required : null),
    );
  }

  String? _required(String? value) {
    return value == null || value.trim().isEmpty ? 'Campo obrigatório' : null;
  }

  String? _emailValidator(String? value) {
    final text = value?.trim() ?? '';
    if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(text)) {
      return 'Email inválido';
    }
    return null;
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    setState(() => _saving = true);
    final controller = ref.read(usersControllerProvider.notifier);
    final user = _isEditing
        ? await controller.updateUser(
            widget.userId!,
            UserUpdateInput(
              email: _email.text.trim(),
              firstName: _firstName.text.trim(),
              lastName: _lastName.text.trim(),
              displayName: _displayName.text.trim().isEmpty
                  ? null
                  : _displayName.text.trim(),
              phone: _phone.text.trim().isEmpty ? null : _phone.text.trim(),
              status: _status,
              mustChangePassword: _mustChangePassword,
            ),
          )
        : await controller.create(
            UserCreateInput(
              tenantId: _tenantId.text.trim(),
              email: _email.text.trim(),
              password: _password.text,
              firstName: _firstName.text.trim(),
              lastName: _lastName.text.trim(),
              displayName: _displayName.text.trim().isEmpty
                  ? null
                  : _displayName.text.trim(),
              phone: _phone.text.trim().isEmpty ? null : _phone.text.trim(),
              mustChangePassword: _mustChangePassword,
            ),
          );
    if (!mounted) {
      return;
    }
    setState(() => _saving = false);
    if (user != null) {
      context.go('${AppRoutes.users}/${user.id}');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Não foi possível salvar o usuário.')),
      );
    }
  }
}
