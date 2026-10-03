# Categories Testing

## Backend

```bash
docker compose --env-file .env.example exec -T backend pytest tests/unit/categories
docker compose --env-file .env.example exec -T backend pytest tests/integration/categories
docker compose --env-file .env.example exec -T backend pytest
```

## Lint Backend

```bash
docker compose --env-file .env.example exec -T backend ruff check app tests migrations
docker compose --env-file .env.example exec -T backend ruff format --check app tests migrations
```

## Flutter

```bash
cd erp-platform/frontend
flutter analyze
flutter test
flutter build web --dart-define=API_BASE_URL=http://localhost:8000
```

## Plataformas

Android, iOS e macOS devem ser validados quando os devices/simuladores estiverem disponíveis no host atual.

Validação REST-002 em 2026-07-31:

- Web: `flutter build web` concluído.
- Android: `flutter build apk --debug` concluído.
- Android Emulator: device apareceu após launch, mas não permaneceu disponível para `flutter run`; `adb` não estava disponível no PATH do host.
- macOS: build bloqueado no CodeSign por atributos `com.apple.fileprovider.fpfs#P`/FinderInfo do workspace sincronizado.
- iOS Simulator: build bloqueado no CodeSign no mesmo contexto de assinatura do workspace sincronizado.
