# Companies Testing

## Backend

```bash
docker compose --env-file .env.example exec -T backend pytest -m unit
docker compose --env-file .env.example exec -T backend pytest -m integration
docker compose --env-file .env.example exec -T backend pytest
docker compose --env-file .env.example exec -T backend ruff check app tests migrations
docker compose --env-file .env.example exec -T backend ruff format --check app tests migrations
```

## Flutter

```bash
docker compose --env-file .env.example exec -T frontend flutter pub get
docker compose --env-file .env.example exec -T frontend flutter analyze
docker compose --env-file .env.example exec -T frontend flutter test
docker compose --env-file .env.example exec -T frontend flutter build web --dart-define=API_BASE_URL=http://localhost:8000
```
