# Testes MFA

Backend:

```bash
cd erp-platform/backend
pytest -m unit
pytest -m integration
pytest
```

Flutter:

```bash
cd erp-platform/frontend
flutter pub get
dart format --set-exit-if-changed lib test integration_test
flutter analyze
flutter test
flutter build web --dart-define=API_BASE_URL=http://localhost:8000
```

Android deve ser validado em device/emulador disponível. iOS e macOS dependem do bloqueio local de CodeSign documentado em DEV-008.
