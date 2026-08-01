import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../core/api/api_error.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_text_field.dart';
import '../../../shared/layouts/responsive_layout.dart';
import '../domain/auth_state.dart';
import 'auth_controller.dart';

final rememberAccessProvider = NotifierProvider<RememberAccessNotifier, bool>(
  RememberAccessNotifier.new,
);

class RememberAccessNotifier extends Notifier<bool> {
  @override
  bool build() => false;

  void update(bool value) {
    state = value;
  }
}

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _tenantController = TextEditingController(text: 'rigaud-demo');
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _tenantController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final rememberAccess = ref.watch(rememberAccessProvider);
    final authState = ref.watch(authControllerProvider);

    ref.listen(authControllerProvider, (previous, next) {
      final isAuthenticated = next.value?.isAuthenticated ?? false;
      if (isAuthenticated && mounted) {
        context.go(AppRoutes.dashboard);
      }
      final requiresMfa = next.value?.requiresMfa ?? false;
      if (requiresMfa && mounted) {
        context.go(AppRoutes.mfaVerify);
      }
    });

    return Scaffold(
      body: SafeArea(
        child: ResponsiveLayout(
          mobile: _LoginForm(
            tenantController: _tenantController,
            emailController: _emailController,
            passwordController: _passwordController,
            rememberAccess: rememberAccess,
            authState: authState,
            isSubmitting: _isSubmitting,
            onRememberChanged: (value) {
              ref.read(rememberAccessProvider.notifier).update(value ?? false);
            },
            onSubmit: _submit,
          ),
          desktop: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: _LoginForm(
                tenantController: _tenantController,
                emailController: _emailController,
                passwordController: _passwordController,
                rememberAccess: rememberAccess,
                authState: authState,
                isSubmitting: _isSubmitting,
                onRememberChanged: (value) {
                  ref
                      .read(rememberAccessProvider.notifier)
                      .update(value ?? false);
                },
                onSubmit: _submit,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _submit() async {
    final tenant = _tenantController.text.trim();
    final email = _emailController.text.trim();
    final password = _passwordController.text;
    if (tenant.isEmpty || email.isEmpty || password.isEmpty) {
      return;
    }

    setState(() => _isSubmitting = true);
    await ref
        .read(authControllerProvider.notifier)
        .login(tenant: tenant, email: email, password: password);
    if (mounted) {
      setState(() => _isSubmitting = false);
    }
  }
}

class _LoginForm extends StatelessWidget {
  const _LoginForm({
    required this.tenantController,
    required this.emailController,
    required this.passwordController,
    required this.rememberAccess,
    required this.authState,
    required this.isSubmitting,
    required this.onRememberChanged,
    required this.onSubmit,
  });

  final TextEditingController tenantController;
  final TextEditingController emailController;
  final TextEditingController passwordController;
  final bool rememberAccess;
  final AsyncValue<AuthState> authState;
  final bool isSubmitting;
  final ValueChanged<bool?> onRememberChanged;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    final error = authState.error;
    final errorMessage = switch (error) {
      ApiError(message: final message) => message,
      Object() => 'Não foi possível autenticar.',
      null => null,
    };

    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              AspectRatio(
                aspectRatio: 1,
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  child: Image.asset(
                    'assets/images/logo_rigaud_tech.png',
                    fit: BoxFit.contain,
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              Text(
                'Rigaud Tech ERP',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                'Acesse sua plataforma de gestão',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: AppSpacing.xl),
              AppTextField(
                controller: tenantController,
                label: 'Tenant',
                prefixIcon: Icons.apartment_outlined,
              ),
              const SizedBox(height: AppSpacing.md),
              AppTextField(
                controller: emailController,
                label: 'Email',
                keyboardType: TextInputType.emailAddress,
                prefixIcon: Icons.email_outlined,
              ),
              const SizedBox(height: AppSpacing.md),
              AppTextField(
                controller: passwordController,
                label: 'Senha',
                obscureText: true,
                prefixIcon: Icons.lock_outline,
              ),
              if (errorMessage != null) ...[
                const SizedBox(height: AppSpacing.sm),
                Text(
                  errorMessage,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              const SizedBox(height: AppSpacing.sm),
              Row(
                children: [
                  Checkbox(value: rememberAccess, onChanged: onRememberChanged),
                  const Expanded(child: Text('Lembrar acesso')),
                  TextButton(
                    onPressed: () {},
                    child: const Text('Recuperar senha'),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              AppButton(
                label: 'Entrar',
                icon: Icons.login,
                isLoading: isSubmitting,
                onPressed: onSubmit,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
