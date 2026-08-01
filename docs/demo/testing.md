# Testes Do Demo Environment

Os testes da DOC-003 validam que o seed é idempotente, que os segmentos podem ser aplicados separadamente e que o reset preserva o tenant da plataforma.

## Backend

Executar apenas os testes do demo:

```bash
docker compose --env-file .env.example run --rm backend pytest tests/integration/demo/test_demo_seed.py
```

Validar API demo:

```bash
curl http://localhost:8000/api/v1/demo/status
curl http://localhost:8000/api/v1/demo/install
curl http://localhost:8000/api/v1/demo/scenarios
curl http://localhost:8000/api/v1/demo/reset
```

Executar a suíte completa do backend:

```bash
docker compose --env-file .env.example run --rm backend pytest
```

Quando a base local tiver recebido `make demo`, limpe antes os tenants demo operacionais:

```bash
make demo-reset
```

O alvo `make test` já executa esse reset antes do pytest para evitar conflito entre dados persistentes de demonstração e fixtures de integração.

Executar lint focado:

```bash
docker compose --env-file .env.example run --rm backend ruff check app/shared/demo tests/integration/demo
```

## Validação Manual

Com a stack ativa:

```bash
make up
make demo
```

Depois acessar o frontend ou Swagger e autenticar com uma conta documentada em `docs/demo/accounts.md`.

Validar o dashboard:

```bash
flutter test
flutter build web
```
