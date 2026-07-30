import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/mfa.dart';
import '../data/mfa_repository_impl.dart';
import '../domain/mfa_repository.dart';

class MfaSettingsState {
  const MfaSettingsState({
    this.status,
    this.totpSetup,
    this.recoveryCodes = const [],
  });

  final MfaStatus? status;
  final TotpSetup? totpSetup;
  final List<String> recoveryCodes;

  MfaSettingsState copyWith({
    MfaStatus? status,
    TotpSetup? totpSetup,
    List<String>? recoveryCodes,
  }) {
    return MfaSettingsState(
      status: status ?? this.status,
      totpSetup: totpSetup ?? this.totpSetup,
      recoveryCodes: recoveryCodes ?? this.recoveryCodes,
    );
  }
}

final mfaControllerProvider =
    AsyncNotifierProvider<MfaController, MfaSettingsState>(MfaController.new);

class MfaController extends AsyncNotifier<MfaSettingsState> {
  MfaRepository get _repository => ref.read(mfaRepositoryProvider);

  @override
  Future<MfaSettingsState> build() async {
    return MfaSettingsState(status: await _repository.status());
  }

  Future<void> setupTotp() async {
    state = await AsyncValue.guard(() async {
      final setup = await _repository.setupTotp();
      return state.value?.copyWith(totpSetup: setup) ??
          MfaSettingsState(totpSetup: setup);
    });
  }

  Future<void> confirmTotp(String code) async {
    state = await AsyncValue.guard(() async {
      final codes = await _repository.confirmTotp(code);
      return MfaSettingsState(
        status: await _repository.status(),
        recoveryCodes: codes,
      );
    });
  }

  Future<void> regenerateRecoveryCodes() async {
    state = await AsyncValue.guard(() async {
      final codes = await _repository.regenerateRecoveryCodes();
      return MfaSettingsState(
        status: await _repository.status(),
        recoveryCodes: codes,
      );
    });
  }

  Future<void> disable(String currentPassword) async {
    state = await AsyncValue.guard(() async {
      await _repository.disable(currentPassword);
      return MfaSettingsState(status: await _repository.status());
    });
  }
}
