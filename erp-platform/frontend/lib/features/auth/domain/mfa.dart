import 'auth_tokens.dart';

class MfaLoginMethod {
  const MfaLoginMethod({
    required this.id,
    required this.type,
    this.destination,
  });

  final String id;
  final String type;
  final String? destination;

  factory MfaLoginMethod.fromJson(Map<String, dynamic> json) {
    return MfaLoginMethod(
      id: json['id'] as String? ?? '',
      type: json['type'] as String? ?? '',
      destination: json['destination'] as String?,
    );
  }
}

class MfaChallenge {
  const MfaChallenge({
    required this.challengeId,
    required this.availableMethods,
    required this.expiresIn,
  });

  final String challengeId;
  final List<MfaLoginMethod> availableMethods;
  final int expiresIn;

  factory MfaChallenge.fromJson(Map<String, dynamic> json) {
    final methods = json['available_methods'] as List<dynamic>? ?? const [];
    return MfaChallenge(
      challengeId: json['challenge_id'] as String? ?? '',
      availableMethods: methods
          .map((item) => MfaLoginMethod.fromJson(item as Map<String, dynamic>))
          .toList(),
      expiresIn: json['expires_in'] as int? ?? 0,
    );
  }
}

class AuthLoginResult {
  const AuthLoginResult.tokens(this.tokens) : mfaChallenge = null;

  const AuthLoginResult.mfaRequired(this.mfaChallenge) : tokens = null;

  final AuthTokens? tokens;
  final MfaChallenge? mfaChallenge;

  bool get requiresMfa => mfaChallenge != null;
}

class MfaMethod {
  const MfaMethod({
    required this.id,
    required this.type,
    required this.status,
    required this.isPrimary,
    this.destination,
  });

  final String id;
  final String type;
  final String status;
  final bool isPrimary;
  final String? destination;

  factory MfaMethod.fromJson(Map<String, dynamic> json) {
    return MfaMethod(
      id: json['id'] as String? ?? '',
      type: json['type'] as String? ?? '',
      status: json['status'] as String? ?? '',
      isPrimary: json['is_primary'] as bool? ?? false,
      destination: json['destination'] as String?,
    );
  }
}

class MfaStatus {
  const MfaStatus({
    required this.state,
    required this.enabled,
    required this.methods,
    required this.recoveryCodesRemaining,
  });

  final String state;
  final bool enabled;
  final List<MfaMethod> methods;
  final int recoveryCodesRemaining;

  factory MfaStatus.fromJson(Map<String, dynamic> json) {
    final methods = json['methods'] as List<dynamic>? ?? const [];
    return MfaStatus(
      state: json['state'] as String? ?? 'disabled',
      enabled: json['enabled'] as bool? ?? false,
      methods: methods
          .map((item) => MfaMethod.fromJson(item as Map<String, dynamic>))
          .toList(),
      recoveryCodesRemaining: json['recovery_codes_remaining'] as int? ?? 0,
    );
  }
}

class TotpSetup {
  const TotpSetup({
    required this.methodId,
    required this.secret,
    required this.otpauthUri,
    required this.issuer,
  });

  final String methodId;
  final String secret;
  final String otpauthUri;
  final String issuer;

  factory TotpSetup.fromJson(Map<String, dynamic> json) {
    return TotpSetup(
      methodId: json['method_id'] as String? ?? '',
      secret: json['secret'] as String? ?? '',
      otpauthUri: json['otpauth_uri'] as String? ?? '',
      issuer: json['issuer'] as String? ?? '',
    );
  }
}
