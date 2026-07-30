import 'user.dart';

class UserCreateInput {
  const UserCreateInput({
    required this.tenantId,
    required this.email,
    required this.password,
    this.firstName,
    this.lastName,
    this.displayName,
    this.phone,
    this.mustChangePassword = true,
  });

  final String tenantId;
  final String email;
  final String password;
  final String? firstName;
  final String? lastName;
  final String? displayName;
  final String? phone;
  final bool mustChangePassword;

  Map<String, dynamic> toJson() => {
    'tenant_id': tenantId,
    'email': email,
    'password': password,
    'first_name': firstName,
    'last_name': lastName,
    'display_name': displayName,
    'phone': phone,
    'must_change_password': mustChangePassword,
  };
}

class UserUpdateInput {
  const UserUpdateInput({
    this.email,
    this.firstName,
    this.lastName,
    this.displayName,
    this.phone,
    this.status,
    this.mustChangePassword,
  });

  final String? email;
  final String? firstName;
  final String? lastName;
  final String? displayName;
  final String? phone;
  final UserStatus? status;
  final bool? mustChangePassword;

  Map<String, dynamic> toJson() => {
    'email': email,
    'first_name': firstName,
    'last_name': lastName,
    'display_name': displayName,
    'phone': phone,
    'status': status?.name,
    'must_change_password': mustChangePassword,
  };
}

class ProfileUpdateInput {
  const ProfileUpdateInput({
    this.firstName,
    this.lastName,
    this.displayName,
    this.phone,
  });

  final String? firstName;
  final String? lastName;
  final String? displayName;
  final String? phone;

  Map<String, dynamic> toJson() => {
    'first_name': firstName,
    'last_name': lastName,
    'display_name': displayName,
    'phone': phone,
  };
}
