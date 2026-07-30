enum UserStatus {
  active,
  inactive,
  blocked;

  String get label {
    return switch (this) {
      UserStatus.active => 'Ativo',
      UserStatus.inactive => 'Inativo',
      UserStatus.blocked => 'Bloqueado',
    };
  }
}

class UserProfile {
  const UserProfile({
    required this.id,
    required this.tenantId,
    required this.tenantSlug,
    required this.email,
    required this.status,
    required this.isActive,
    required this.isSuperuser,
    required this.mustChangePassword,
    this.firstName,
    this.lastName,
    this.displayName,
    this.phone,
    this.lastLoginAt,
  });

  final String id;
  final String tenantId;
  final String tenantSlug;
  final String email;
  final String? firstName;
  final String? lastName;
  final String? displayName;
  final String? phone;
  final UserStatus status;
  final bool isActive;
  final bool isSuperuser;
  final bool mustChangePassword;
  final DateTime? lastLoginAt;

  String get title => displayName?.isNotEmpty == true
      ? displayName!
      : [firstName, lastName].whereType<String>().join(' ').trim().isEmpty
      ? email
      : [firstName, lastName].whereType<String>().join(' ').trim();

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String? ?? '',
      tenantId: json['tenant_id'] as String? ?? '',
      tenantSlug: json['tenant_slug'] as String? ?? '',
      email: json['email'] as String? ?? '',
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      displayName: json['display_name'] as String?,
      phone: json['phone'] as String?,
      status: UserStatus.values.byName(json['status'] as String? ?? 'inactive'),
      isActive: json['is_active'] as bool? ?? false,
      isSuperuser: json['is_superuser'] as bool? ?? false,
      mustChangePassword: json['must_change_password'] as bool? ?? false,
      lastLoginAt: DateTime.tryParse(json['last_login_at'] as String? ?? ''),
    );
  }
}

class UserPage {
  const UserPage({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  final List<UserProfile> items;
  final int total;
  final int page;
  final int pageSize;

  factory UserPage.fromJson(Map<String, dynamic> json) {
    final items = json['items'] as List<dynamic>? ?? [];
    return UserPage(
      items: items
          .map((item) => UserProfile.fromJson(item as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      pageSize: json['page_size'] as int? ?? 20,
    );
  }
}
