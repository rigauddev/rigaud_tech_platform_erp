# Backend Starter

Base inicial do backend da Rigaud Tech Platform ERP.

Esta documentação cobre somente a fundação técnica da DEV-002. Nenhuma regra de negócio, entidade, CRUD ou endpoint funcional do ERP foi implementado.

## Tecnologias

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic v2
- Pytest
- JWT
- PostgreSQL
- Docker
- Async/Await
- Dependency Injection
- Clean Architecture
- Repository Pattern
- Use Case Pattern
- DDD simplificado

## Estrutura

- `app`: pacote principal da aplicação.
- `app/api`: roteamento HTTP, versionamento e health check.
- `app/core`: configuração por ambiente, settings, logs, OpenAPI e compatibilidade interna.
- `app/database`: SQLAlchemy 2.x assíncrono, engine, sessão e base declarativa.
- `app/middlewares`: request id, logging, CORS e compression.
- `app/exceptions`: handlers globais de erro.
- `app/security`: preparação para JWT, hash de senha, RBAC e MFA.
- `app/utils`: utilitários técnicos compartilhados.
- `app/modules`: módulos independentes com camadas internas.
- `app/shared`: contratos reutilizáveis entre módulos.
- `requirements`: dependências por perfil para ferramentas baseadas em requirements.
- `tests`: testes automatizados.
- `migrations`: estrutura Alembic de migrations.

## API

- Swagger: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
- Health Check: `/health`
- Health Check versionado: `/api/v1/health`

## Banco

O SQLAlchemy está configurado com engine assíncrona, sessão assíncrona e `Base` declarativa.

Na DEV-004, o Alembic passou a executar migrations assíncronas e recebeu a migration técnica inicial.

Nenhuma entidade de negócio foi criada.

## Segurança

A camada de segurança contém apenas preparação técnica para:

- JWT
- Password hash
- RBAC
- MFA

Nenhum fluxo de autenticação foi implementado.

## Logs e middlewares

O backend registra logs estruturados e separa os loggers:

- `application`
- `errors`
- `audit`

Middlewares preparados:

- RequestId
- Logging
- CORS
- Compression

## Testes

O Pytest está configurado no `pyproject.toml`.

Teste inicial criado:

- `GET /health`

## Observações

Esta task cria somente a estrutura base do backend.
