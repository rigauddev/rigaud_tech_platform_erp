# Database Core

Fundação técnica de persistência criada na DEV-004.

Esta etapa prepara PostgreSQL 16, SQLAlchemy 2.x assíncrono, Alembic e testes de integração sem criar entidades de negócio.

## Componentes

- `app/database/base.py`: base declarativa com convenção de nomes.
- `app/database/session.py`: engine assíncrona, factory de sessão e check de conexão.
- `app/database/mixins.py`: mixins reutilizáveis para UUID, tenant, timestamps, exclusão lógica e auditoria básica.
- `app/database/types.py`: tipos compartilhados para UUID.
- `app/database/tenant.py`: contexto técnico de tenant com `contextvars`.
- `app/shared/infrastructure/repository.py`: repositório SQLAlchemy assíncrono base.
- `app/shared/infrastructure/unit_of_work.py`: Unit of Work assíncrona.
- `migrations/env.py`: Alembic assíncrono.
- `migrations/versions/0001_database_core.py`: migration técnica inicial.

## Multi-tenancy

O backend está preparado para multi-tenancy por `tenant_id`.

O `TenantMixin` adiciona a coluna `tenant_id` para futuras entidades e `app/database/tenant.py` mantém o tenant corrente em contexto assíncrono.

Nenhuma regra de seleção automática por tenant foi implementada nesta task.

## Mixins

- `UUIDPrimaryKeyMixin`: chave primária UUID.
- `TenantMixin`: coluna `tenant_id`.
- `TimestampMixin`: `created_at` e `updated_at`.
- `SoftDeleteMixin`: `deleted_at` e propriedade `is_deleted`.
- `AuditMixin`: `created_by`, `updated_by` e `deleted_by` como UUIDs opcionais.
- `CoreEntityMixin`: composição dos mixins técnicos.

## Migration técnica inicial

A migration `0001_database_core` cria:

- extensão PostgreSQL `pgcrypto`, usada futuramente para suporte a UUID no banco.

Nenhuma tabela de negócio ou tabela artificial é criada.

## Health check do banco

Rotas técnicas:

- `GET /health/database`
- `GET /api/v1/health/database`

Resposta esperada:

```json
{
  "status": "healthy",
  "database": "reachable"
}
```

## Comandos

Rodar migrations:

```bash
make db-current
make db-history
make db-revision name="descricao"
make db-upgrade
make db-downgrade
```

Executar testes do backend:

```bash
make test
```

Executar somente testes de banco dentro do container backend:

```bash
docker compose --env-file .env.example exec backend pytest tests/test_database_core.py tests/integration/test_database_connection.py
```

## Backup e restauração

O Docker já possui volume persistente para dados e volume reservado para backups futuros.

Rotinas de backup, restore, retenção e automação não foram implementadas nesta task.
