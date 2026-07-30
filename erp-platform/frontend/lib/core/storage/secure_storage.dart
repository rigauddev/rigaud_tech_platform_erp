import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/services.dart';

final secureStorageProvider = Provider<SecureStorage>((ref) {
  return SecureStorage(const FlutterSecureStorage());
});

class SecureStorage {
  SecureStorage(this._storage);

  final FlutterSecureStorage _storage;
  final Map<String, String> _memoryFallback = {};

  Future<String?> readAccessToken() {
    return _read('access_token');
  }

  Future<String?> readRefreshToken() {
    return _read('refresh_token');
  }

  Future<void> writeTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _write('access_token', accessToken);
    await _write('refresh_token', refreshToken);
  }

  Future<void> clearTokens() async {
    await _delete('access_token');
    await _delete('refresh_token');
  }

  Future<String?> _read(String key) async {
    try {
      return await _storage.read(key: key);
    } on MissingPluginException {
      return _memoryFallback[key];
    }
  }

  Future<void> _write(String key, String value) async {
    try {
      await _storage.write(key: key, value: value);
    } on MissingPluginException {
      _memoryFallback[key] = value;
    }
  }

  Future<void> _delete(String key) async {
    try {
      await _storage.delete(key: key);
    } on MissingPluginException {
      _memoryFallback.remove(key);
    }
  }
}
