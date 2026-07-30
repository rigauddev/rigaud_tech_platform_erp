class AuthUser {
  const AuthUser({
    required this.id,
    required this.tenantId,
    required this.email,
    required this.isActive,
    required this.isSuperuser,
    this.membershipId,
    this.branchId,
    this.branchMembershipId,
    this.role,
    this.accessScope,
  });

  final String id;
  final String tenantId;
  final String email;
  final bool isActive;
  final bool isSuperuser;
  final String? membershipId;
  final String? branchId;
  final String? branchMembershipId;
  final String? role;
  final String? accessScope;
}
