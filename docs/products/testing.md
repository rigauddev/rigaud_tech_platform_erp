# Products Testing

Validações previstas para REST-001:

```bash
docker compose config
docker compose up -d postgres redis backend
alembic current
alembic history
alembic upgrade head
pytest -m unit
pytest -m integration
pytest
ruff check .
ruff format --check .
make lint
make test
make format
make check-task TASK=REST-001
```

Flutter:

```bash
flutter pub get
dart format --set-exit-if-changed lib test integration_test
flutter analyze
flutter test
flutter build web --dart-define=API_BASE_URL=http://localhost:8000
flutter doctor -v
flutter devices
```

Execução por plataforma:

```bash
flutter emulators
flutter emulators --launch Pixel_9_Pro_XL
flutter run -d emulator-5554 --dart-define=API_BASE_URL=http://10.0.2.2:8000
flutter run -d 7586BC75-ACFF-4479-BFE0-934F37F1A3D6 --dart-define=API_BASE_URL=http://localhost:8000
flutter run -d macos --dart-define=API_BASE_URL=http://localhost:8000
```

Quando alternar entre comandos Flutter no container e comandos Flutter locais, execute novamente:

```bash
flutter pub get
```

Isso recria `.dart_tool/package_config.json` com os caminhos do SDK local, evitando que builds locais de Android, iOS e macOS tentem usar caminhos internos do container.

Windows não deve ser declarado como validado em macOS.

iOS e macOS dependem do estado local de CodeSign. Em workspaces dentro de pastas sincronizadas por File Provider/iCloud, o Xcode pode falhar com `resource fork, Finder information, or similar detritus not allowed`. A validação local deve usar uma cópia fora da pasta sincronizada ou um workspace movido para um diretório local não sincronizado.
