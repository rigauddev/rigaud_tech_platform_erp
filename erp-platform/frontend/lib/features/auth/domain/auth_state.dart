import 'auth_user.dart';
import 'mfa.dart';

class AuthState {
  const AuthState({
    required this.isAuthenticated,
    this.user,
    this.mfaChallenge,
  });

  const AuthState.unauthenticated()
    : isAuthenticated = false,
      user = null,
      mfaChallenge = null;

  const AuthState.authenticated(this.user)
    : isAuthenticated = true,
      mfaChallenge = null;

  const AuthState.mfaRequired(this.mfaChallenge)
    : isAuthenticated = false,
      user = null;

  final bool isAuthenticated;
  final AuthUser? user;
  final MfaChallenge? mfaChallenge;

  bool get requiresMfa => mfaChallenge != null;
}
