import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../storage/preferences_storage.dart';

enum AppLanguage {
  portuguese('pt', 'Português'),
  english('en', 'English');

  const AppLanguage(this.code, this.label);

  final String code;
  final String label;

  Locale get locale => Locale(code);
}

final appLanguageProvider =
    NotifierProvider<AppLanguageController, AppLanguage>(
      AppLanguageController.new,
    );

class AppLanguageController extends Notifier<AppLanguage> {
  @override
  AppLanguage build() {
    ref.listen<AsyncValue<PreferencesStorage>>(preferencesStorageProvider, (
      previous,
      next,
    ) {
      next.whenData((storage) {
        final savedCode = storage.locale;
        final savedLanguage = AppLanguage.values.where(
          (language) => language.code == savedCode,
        );
        if (savedLanguage.isNotEmpty &&
            state.code != savedLanguage.first.code) {
          state = savedLanguage.first;
        }
      });
    });
    return AppLanguage.portuguese;
  }

  void select(AppLanguage language) {
    state = language;
    unawaited(
      ref
          .read(preferencesStorageProvider.future)
          .then((storage) => storage.setLocale(language.code)),
    );
  }
}
