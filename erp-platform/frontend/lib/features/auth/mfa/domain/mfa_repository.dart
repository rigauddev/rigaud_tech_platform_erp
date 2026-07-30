import '../../domain/mfa.dart';

abstract interface class MfaRepository {
  Future<MfaStatus> status();

  Future<TotpSetup> setupTotp();

  Future<List<String>> confirmTotp(String code);

  Future<List<String>> regenerateRecoveryCodes();

  Future<void> disable(String currentPassword);
}
