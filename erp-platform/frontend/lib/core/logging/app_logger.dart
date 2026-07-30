import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logging/logging.dart';

import '../../app/config/app_config_provider.dart';

final appLoggerProvider = Provider<Logger>((ref) {
  final config = ref.watch(appConfigProvider);
  final logger = Logger('rigaud_tech_erp');

  Logger.root.level = Level.LEVELS.firstWhere(
    (level) => level.name == config.logLevel,
    orElse: () => Level.INFO,
  );

  return logger;
});
