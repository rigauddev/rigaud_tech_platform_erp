import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../data/user_repository_impl.dart';

class ChangeMyPasswordScreen extends ConsumerStatefulWidget {
  const ChangeMyPasswordScreen({super.key});

  @override
  ConsumerState<ChangeMyPasswordScreen> createState() =>
      _ChangeMyPasswordScreenState();
}

class _ChangeMyPasswordScreenState
    extends ConsumerState<ChangeMyPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _currentPassword = TextEditingController();
  final _newPassword = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _currentPassword.dispose();
    _newPassword.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Alterar senha',
      selectedIndex: 2,
      body: _PasswordForm(
        formKey: _formKey,
        currentPassword: _currentPassword,
        newPassword: _newPassword,
        saving: _saving,
        onSave: _save,
      ),
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    setState(() => _saving = true);
    try {
      await ref
          .read(userRepositoryProvider)
          .changePassword(
            currentPassword: _currentPassword.text,
            newPassword: _newPassword.text,
          );
      if (mounted) {
        context.go(AppRoutes.login);
      }
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }
}

class ResetUserPasswordScreen extends ConsumerStatefulWidget {
  const ResetUserPasswordScreen({required this.userId, super.key});

  final String userId;

  @override
  ConsumerState<ResetUserPasswordScreen> createState() =>
      _ResetUserPasswordScreenState();
}

class _ResetUserPasswordScreenState
    extends ConsumerState<ResetUserPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _temporaryPassword = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _temporaryPassword.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Resetar senha',
      selectedIndex: 2,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _temporaryPassword,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Senha temporária',
                ),
                validator: _passwordValidator,
              ),
              const SizedBox(height: AppSpacing.lg),
              Align(
                alignment: Alignment.centerRight,
                child: AppButton(
                  label: 'Salvar',
                  icon: Icons.key_outlined,
                  isLoading: _saving,
                  onPressed: _save,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    setState(() => _saving = true);
    try {
      await ref
          .read(userRepositoryProvider)
          .resetPassword(
            id: widget.userId,
            temporaryPassword: _temporaryPassword.text,
          );
      if (mounted) {
        context.go('${AppRoutes.users}/${widget.userId}');
      }
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }
}

class _PasswordForm extends StatelessWidget {
  const _PasswordForm({
    required this.formKey,
    required this.currentPassword,
    required this.newPassword,
    required this.saving,
    required this.onSave,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController currentPassword;
  final TextEditingController newPassword;
  final bool saving;
  final VoidCallback onSave;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Form(
        key: formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextFormField(
              controller: currentPassword,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Senha atual'),
              validator: (value) =>
                  value == null || value.isEmpty ? 'Campo obrigatório' : null,
            ),
            const SizedBox(height: AppSpacing.md),
            TextFormField(
              controller: newPassword,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Nova senha'),
              validator: _passwordValidator,
            ),
            const SizedBox(height: AppSpacing.lg),
            Align(
              alignment: Alignment.centerRight,
              child: AppButton(
                label: 'Salvar',
                icon: Icons.save_outlined,
                isLoading: saving,
                onPressed: onSave,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

String? _passwordValidator(String? value) {
  final text = value ?? '';
  if (text.length < 8) {
    return 'Senha deve ter ao menos 8 caracteres';
  }
  return null;
}
