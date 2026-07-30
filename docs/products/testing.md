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

Windows não deve ser declarado como validado em macOS.

iOS e macOS dependem do estado local de CodeSign.
