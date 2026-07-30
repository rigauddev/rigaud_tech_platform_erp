# Database Testing

Testes do banco cobrem a fundação técnica da persistência.

## Comandos

```bash
pytest
pytest -m unit
pytest -m integration
```

Via Docker:

```bash
docker compose --env-file .env.example exec backend pytest
docker compose --env-file .env.example exec backend pytest -m unit
docker compose --env-file .env.example exec backend pytest -m integration
```

## Isolamento

Testes unitários não dependem de serviços externos.

Testes de integração exigem PostgreSQL acessível e não devem executar operações destrutivas fora de banco explicitamente identificado como ambiente de teste.

## Diagnóstico

```bash
docker compose --env-file .env.example ps postgres
docker compose --env-file .env.example logs postgres
curl http://localhost:8000/health/database
```
