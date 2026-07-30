import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../../../app/theme/app_spacing.dart';
import '../../../../shared/components/app_button.dart';
import '../../../../shared/components/app_error_view.dart';
import '../../../../shared/components/app_loading.dart';
import '../../../../shared/layouts/app_scaffold.dart';
import 'mfa_controller.dart';

class MfaSettingsScreen extends ConsumerStatefulWidget {
  const MfaSettingsScreen({super.key});

  @override
  ConsumerState<MfaSettingsScreen> createState() => _MfaSettingsScreenState();
}

class _MfaSettingsScreenState extends ConsumerState<MfaSettingsScreen> {
  final _totpCodeController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _totpCodeController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(mfaControllerProvider);
    return AppScaffold(
      title: 'Autenticação em dois fatores',
      selectedIndex: 3,
      body: state.when(
        loading: () => const AppLoading(),
        error: (error, stackTrace) => AppErrorView(message: error.toString()),
        data: (data) => ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            _StatusPanel(enabled: data.status?.enabled ?? false),
            const SizedBox(height: AppSpacing.lg),
            Wrap(
              spacing: AppSpacing.md,
              runSpacing: AppSpacing.md,
              children: [
                AppButton(
                  label: 'Configurar aplicativo autenticador',
                  icon: Icons.qr_code_2_outlined,
                  onPressed: () =>
                      ref.read(mfaControllerProvider.notifier).setupTotp(),
                ),
                AppButton(
                  label: 'Regenerar códigos',
                  icon: Icons.key_outlined,
                  onPressed: () => ref
                      .read(mfaControllerProvider.notifier)
                      .regenerateRecoveryCodes(),
                ),
              ],
            ),
            if (data.totpSetup != null) ...[
              const SizedBox(height: AppSpacing.xl),
              Center(
                child: QrImageView(
                  data: data.totpSetup!.otpauthUri,
                  version: QrVersions.auto,
                  size: 220,
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              SelectableText(
                data.totpSetup!.secret,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppSpacing.sm),
              TextButton.icon(
                onPressed: () => Clipboard.setData(
                  ClipboardData(text: data.totpSetup!.secret),
                ),
                icon: const Icon(Icons.copy_outlined),
                label: const Text('Copiar chave manual'),
              ),
              const SizedBox(height: AppSpacing.md),
              TextField(
                controller: _totpCodeController,
                decoration: const InputDecoration(
                  labelText: 'Código do aplicativo',
                ),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: AppSpacing.md),
              AppButton(
                label: 'Confirmar aplicativo',
                icon: Icons.check_circle_outline,
                onPressed: () => ref
                    .read(mfaControllerProvider.notifier)
                    .confirmTotp(_totpCodeController.text.trim()),
              ),
            ],
            if (data.recoveryCodes.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xl),
              Text(
                'Códigos de recuperação',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: AppSpacing.sm),
              ...data.recoveryCodes.map(
                (code) => ListTile(
                  leading: const Icon(Icons.key_outlined),
                  title: SelectableText(code),
                  trailing: IconButton(
                    icon: const Icon(Icons.copy_outlined),
                    onPressed: () =>
                        Clipboard.setData(ClipboardData(text: code)),
                  ),
                ),
              ),
            ],
            const SizedBox(height: AppSpacing.xl),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Senha atual'),
              obscureText: true,
            ),
            const SizedBox(height: AppSpacing.md),
            AppButton(
              label: 'Desabilitar 2FA',
              icon: Icons.security_update_warning_outlined,
              onPressed: () => ref
                  .read(mfaControllerProvider.notifier)
                  .disable(_passwordController.text),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusPanel extends StatelessWidget {
  const _StatusPanel({required this.enabled});

  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(enabled ? Icons.verified_user : Icons.shield_outlined),
      title: Text(enabled ? '2FA habilitado' : '2FA desabilitado'),
      subtitle: const Text(
        'TOTP é o canal recomendado. Email e SMS dependem do provedor.',
      ),
    );
  }
}
