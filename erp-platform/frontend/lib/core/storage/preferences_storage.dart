import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

final preferencesStorageProvider = FutureProvider<PreferencesStorage>((
  ref,
) async {
  final preferences = await SharedPreferences.getInstance();
  return PreferencesStorage(preferences);
});

class PreferencesStorage {
  const PreferencesStorage(this._preferences);

  final SharedPreferences _preferences;

  String? get theme => _preferences.getString('theme');
  Future<bool> setTheme(String value) => _preferences.setString('theme', value);

  String? get locale => _preferences.getString('locale');
  Future<bool> setLocale(String value) =>
      _preferences.setString('locale', value);

  String? get selectedTenant => _preferences.getString('selected_tenant');
  Future<bool> setSelectedTenant(String value) {
    return _preferences.setString('selected_tenant', value);
  }

  bool get rememberAccess => _preferences.getBool('remember_access') ?? false;
  Future<bool> setRememberAccess(bool value) {
    return _preferences.setBool('remember_access', value);
  }
}
