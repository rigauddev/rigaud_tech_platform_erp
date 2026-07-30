import 'user.dart';
import 'user_input.dart';

abstract interface class UserRepository {
  Future<UserPage> list({
    int page = 1,
    int pageSize = 20,
    String? companyId,
    UserStatus? status,
    String? search,
  });

  Future<UserProfile> get(String id);

  Future<UserProfile> me();

  Future<UserProfile> create(UserCreateInput input);

  Future<UserProfile> update(String id, UserUpdateInput input);

  Future<UserProfile> updateMe(ProfileUpdateInput input);

  Future<UserProfile> activate(String id);

  Future<UserProfile> deactivate(String id);

  Future<UserProfile> block(String id);

  Future<UserProfile> unblock(String id);

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  });

  Future<void> resetPassword({
    required String id,
    required String temporaryPassword,
  });
}
