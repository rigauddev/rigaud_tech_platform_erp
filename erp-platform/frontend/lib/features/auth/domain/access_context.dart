class ActiveAccessContext {
  const ActiveAccessContext({
    required this.tenantId,
    this.membershipId,
    this.branchId,
    this.branchMembershipId,
    this.role,
    this.accessScope,
  });

  final String tenantId;
  final String? membershipId;
  final String? branchId;
  final String? branchMembershipId;
  final String? role;
  final String? accessScope;

  factory ActiveAccessContext.fromJson(Map<String, dynamic> json) {
    return ActiveAccessContext(
      tenantId: json['tenant_id'] as String? ?? '',
      membershipId: json['membership_id'] as String?,
      branchId: json['branch_id'] as String?,
      branchMembershipId: json['branch_membership_id'] as String?,
      role: json['role'] as String?,
      accessScope: json['access_scope'] as String?,
    );
  }
}

class BranchAccess {
  const BranchAccess({
    required this.id,
    required this.branchId,
    required this.role,
    required this.status,
    required this.isDefault,
  });

  final String id;
  final String branchId;
  final String role;
  final String status;
  final bool isDefault;

  factory BranchAccess.fromJson(Map<String, dynamic> json) {
    return BranchAccess(
      id: json['id'] as String? ?? '',
      branchId: json['branch_id'] as String? ?? '',
      role: json['role'] as String? ?? '',
      status: json['status'] as String? ?? '',
      isDefault: json['is_default'] as bool? ?? false,
    );
  }
}

class CompanyAccess {
  const CompanyAccess({
    required this.id,
    required this.tenantId,
    required this.role,
    required this.status,
    required this.accessScope,
    required this.isDefault,
    required this.branches,
  });

  final String id;
  final String tenantId;
  final String role;
  final String status;
  final String accessScope;
  final bool isDefault;
  final List<BranchAccess> branches;

  factory CompanyAccess.fromJson(Map<String, dynamic> json) {
    final branches = json['branches'] as List<dynamic>? ?? const [];
    return CompanyAccess(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      role: json['role'] as String? ?? '',
      status: json['status'] as String? ?? '',
      accessScope: json['access_scope'] as String? ?? '',
      isDefault: json['is_default'] as bool? ?? false,
      branches: branches
          .map((item) => BranchAccess.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class ContextOptions {
  const ContextOptions({
    required this.activeContext,
    required this.memberships,
  });

  final ActiveAccessContext activeContext;
  final List<CompanyAccess> memberships;

  factory ContextOptions.fromJson(Map<String, dynamic> json) {
    final memberships = json['memberships'] as List<dynamic>? ?? const [];
    return ContextOptions(
      activeContext: ActiveAccessContext.fromJson(
        json['active_context'] as Map<String, dynamic>? ?? const {},
      ),
      memberships: memberships
          .map((item) => CompanyAccess.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class ContextAccessToken {
  const ContextAccessToken({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
    required this.activeContext,
  });

  final String accessToken;
  final String tokenType;
  final int expiresIn;
  final ActiveAccessContext activeContext;

  factory ContextAccessToken.fromJson(Map<String, dynamic> json) {
    return ContextAccessToken(
      accessToken: json['access_token'] as String? ?? '',
      tokenType: json['token_type'] as String? ?? 'bearer',
      expiresIn: json['expires_in'] as int? ?? 0,
      activeContext: ActiveAccessContext.fromJson(
        json['active_context'] as Map<String, dynamic>? ?? const {},
      ),
    );
  }
}
