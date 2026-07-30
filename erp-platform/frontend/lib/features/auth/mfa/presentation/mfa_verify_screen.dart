import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/router/app_routes.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../core/api/api_error.dart';
import '../../../../shared/components/app_button.dart';
import '../../../../shared/components/app_text_field.dart';
import '../../presentation/auth_controller.dart';

class MfaVerifyScreen extends ConsumerStatefulWidget {
  const MfaVerifyScreen({super.key});

  @override
  ConsumerState<MfaVerifyScreen> createState() => _MfaVerifyScreenState();
}

class _MfaVerifyScreenState extends ConsumerState<MfaVerifyScreen> {
  final _codeController = TextEditingController();
  String? _method;

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final challenge = authState.value?.mfaChallenge;
    final methods = challenge?.availableMethods ?? const [];
    _method ??= methods.isNotEmpty ? methods.first.type : null;

    ref.listen(authControllerProvider, (previous, next) {
      if ((next.value?.isAuthenticated ?? false) && mounted) {
        context.go(AppRoutes.dashboard);
      }
    });

    if (challenge == null) {
      return const Scaffold(body: Center(child: Text('Desafio expirado.')));
    }

    final error = authState.error;
    final errorMessage = switch (error) {
      ApiError(message: final message, requestId: final requestId) =>
        requestId == null ? message : '$message Request ID: $requestId',
      Object() => 'Não foi possível validar o código.',
      null => null,
    };

    return Scaffold(
      appBar: AppBar(
        title: const Text('Autenticação em dois fatores'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () {
            ref.read(authControllerProvider.notifier).cancelMfa();
            context.go(AppRoutes.login);
          },
        ),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: ListView(
              padding: const EdgeInsets.all(AppSpacing.lg),
              children: [
                const Icon(Icons.verified_user_outlined, size: 56),
                const SizedBox(height: AppSpacing.lg),
                DropdownButtonFormField<String>(
                  initialValue: _method,
                  decoration: const InputDecoration(labelText: 'Método'),
                  items: methods
                      .map(
                        (method) => DropdownMenuItem(
                          value: method.type,
                          child: Text(_label(method.type, method.destination)),
                        ),
                      )
                      .toList(),
                  onChanged: (value) => setState(() => _method = value),
                ),
                const SizedBox(height: AppSpacing.md),
                AppTextField(
                  controller: _codeController,
                  label: 'Código de verificação',
                  keyboardType: TextInputType.number,
                  prefixIcon: Icons.password_outlined,
                ),
                if (errorMessage != null) ...[
                  const SizedBox(height: AppSpacing.sm),
                  Text(
                    errorMessage,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ],
                const SizedBox(height: AppSpacing.lg),
                AppButton(
                  label: 'Verificar',
                  icon: Icons.check_circle_outline,
                  isLoading: authState.isLoading,
                  onPressed: () {
                    final method = _method;
                    if (method == null || _codeController.text.trim().isEmpty) {
                      return;
                    }
                    ref
                        .read(authControllerProvider.notifier)
                        .verifyMfa(
                          challengeId: challenge.challengeId,
                          method: method,
                          code: _codeController.text.trim(),
                        );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _label(String type, String? destination) {
    return switch (type) {
      'totp' => 'Aplicativo autenticador',
      'email' => 'Email ${destination ?? ''}',
      'sms' => 'SMS ${destination ?? ''}',
      'recovery_code' => 'Código de recuperação',
      _ => type,
    };
  }
}
