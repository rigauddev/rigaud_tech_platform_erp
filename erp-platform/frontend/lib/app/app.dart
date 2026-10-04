import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:responsive_framework/responsive_framework.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'config/app_config_provider.dart';
import 'router/app_router.dart';
import 'theme/app_theme.dart';
import '../core/constants/app_breakpoints.dart';
import '../core/localization/app_language.dart';

class RigaudTechErpApp extends ConsumerWidget {
  const RigaudTechErpApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config = ref.watch(appConfigProvider);
    final router = ref.watch(appRouterProvider);
    final language = ref.watch(appLanguageProvider);

    return MaterialApp.router(
      title: config.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.light,
      locale: language.locale,
      supportedLocales: AppLanguage.values.map((item) => item.locale),
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      routerConfig: router,
      themeAnimationDuration: Duration.zero,
      themeAnimationCurve: Curves.linear,
      builder: (context, child) {
        return ResponsiveBreakpoints.builder(
          child: child ?? const SizedBox.shrink(),
          breakpoints: AppBreakpoints.values,
        );
      },
    );
  }
}
