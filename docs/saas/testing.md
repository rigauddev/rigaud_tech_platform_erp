# SaaS Testing

## Backend

```bash
docker compose --env-file .env.example exec -T backend pytest tests/unit/saas
docker compose --env-file .env.example exec -T backend pytest tests/integration/saas
docker compose --env-file .env.example exec -T backend pytest
docker compose --env-file .env.example exec -T backend ruff check app tests migrations
docker compose --env-file .env.example exec -T backend ruff format --check app tests migrations
```

## Flutter

DEV-011 não adiciona UI Flutter.

Executar regressão:

```bash
cd erp-platform/frontend
flutter analyze
flutter test
flutter build web --dart-define=API_BASE_URL=http://localhost:8000
```
