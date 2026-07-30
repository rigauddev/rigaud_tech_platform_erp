# ERP Platform Backend

Backend da Rigaud Tech Platform ERP.

Esta estrutura foi preparada com Python 3.13, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, JWT, PostgreSQL, Docker, Clean Architecture, Repository Pattern, Use Case Pattern e DDD simplificado.

Até DEV-006, o backend contém fundações técnicas de autenticação, banco e empresas como raiz do tenant.

## Estrutura principal

- `app/api`: rotas HTTP e versionamento da API.
- `app/core`: configuração por ambiente, logging, OpenAPI e compatibilidade interna.
- `app/database`: base SQLAlchemy 2.x, engine e sessão assíncrona.
- `app/db`: compatibilidade para imports antigos de banco.
- `app/middlewares`: request id, logging, CORS e compression.
- `app/exceptions`: tratamento global de exceções.
- `app/security`: preparação para JWT, password hash, RBAC e MFA.
- `app/utils`: utilitários técnicos compartilhados.
- `app/shared`: contratos e blocos reutilizáveis sem domínio específico.
- `app/modules`: módulos independentes da aplicação.
- `requirements`: dependências por perfil.
- `migrations`: estrutura Alembic de migrations.
- `tests`: testes automatizados.
- `docker`: arquivos auxiliares de container, quando necessários.

## API

- Health check: `/health`
- Health check versionado: `/api/v1/health`
- Swagger: `/docs`
- OpenAPI JSON: `/openapi.json`
- Database health check: `/health/database`

## Ambientes

Use os arquivos `.env.*.example` como base para configurar `local`, `test` e `production`.

## Docker

A orquestração principal de desenvolvimento fica no `docker-compose.yml` da raiz do workspace.

Use `make up` a partir da raiz para subir backend, PostgreSQL, Redis, Mailpit, PgAdmin, Flutter Web e Nginx.

O Dockerfile de desenvolvimento do backend fica em `docker/backend/Dockerfile`.

## Banco de dados

A fundação técnica de banco está documentada em `docs/backend/database-core.md`.

Rodar migrations:

```bash
make shell-backend
alembic upgrade head
```
