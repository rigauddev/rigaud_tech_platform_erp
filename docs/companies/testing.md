# Companies Testing

## Backend

```bash
docker compose --env-file .env.example exec -T backend pytest -m unit
docker compose --env-file .env.example exec -T backend pytest -m integration
docker compose --env-file .env.example exec -T backend pytest tests/integration/companies/test_tenant_context_api.py
docker compose --env-file .env.example exec -T backend pytest
docker compose --env-file .env.example exec -T backend ruff check app tests migrations
docker compose --env-file .env.example exec -T backend ruff format --check app tests migrations
```

`tests/integration/companies/test_tenant_context_api.py` cobre:

- criação automática de matriz;
- contexto padrão no login;
- troca para filial autorizada;
- bloqueio de filial não autorizada;
- troca para segunda empresa autorizada;
- rejeição de branch membership cross-tenant;
- refresh com membership inativo;
- contexto `all_branches` sem `branch_id`.

## Flutter

```bash
docker compose --env-file .env.example exec -T frontend flutter pub get
docker compose --env-file .env.example exec -T frontend flutter analyze
docker compose --env-file .env.example exec -T frontend flutter test
docker compose --env-file .env.example exec -T frontend flutter build web --dart-define=API_BASE_URL=http://localhost:8000
```
