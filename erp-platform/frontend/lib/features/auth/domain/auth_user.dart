class AuthUser {
  const AuthUser({
    required this.id,
    required this.tenantId,
    required this.email,
    required this.isActive,
    required this.isSuperuser,
  });

  final String id;
  final String tenantId;
  final String email;
  final bool isActive;
  final bool isSuperuser;
}
