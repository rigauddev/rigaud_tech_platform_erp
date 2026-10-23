import 'app_environment.dart';

class AppConfig {
  const AppConfig({
    required this.appName,
    required this.environment,
    required this.apiBaseUrl,
    required this.logLevel,
    this.publicAppUrl = '',
  });

  factory AppConfig.fromEnvironment() {
    return AppConfig(
      appName: const String.fromEnvironment(
        'APP_NAME',
        defaultValue: 'Rigaud Tech ERP',
      ),
      environment: AppEnvironment.fromName(
        const String.fromEnvironment('APP_ENV', defaultValue: 'development'),
      ),
      apiBaseUrl: const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://localhost:8000',
      ),
      publicAppUrl: const String.fromEnvironment('PUBLIC_APP_URL'),
      logLevel: const String.fromEnvironment('LOG_LEVEL', defaultValue: 'INFO'),
    );
  }

  final String appName;
  final AppEnvironment environment;
  final String apiBaseUrl;
  final String publicAppUrl;
  final String logLevel;

  bool get isDevelopment => environment == AppEnvironment.development;
}
