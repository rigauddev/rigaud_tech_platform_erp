# Database Core

A fundação de banco do ERP usa PostgreSQL, SQLAlchemy assíncrono e Alembic.

## Por que SQLAlchemy assíncrono

FastAPI trabalha bem com `async/await`. Usar SQLAlchemy assíncrono permite que operações de banco não bloqueiem o loop da aplicação enquanto esperam I/O.

## Base declarativa

A base declarativa centraliza metadata e convenções de nomes.

Isso ajuda Alembic a gerar nomes previsíveis para constraints, índices e chaves.

## Multi-tenancy por tenant_id

O sistema será preparado para separar dados por `tenant_id`.

Nesta etapa, apenas a fundação técnica foi criada:

- mixin com coluna `tenant_id`.
- contexto assíncrono para tenant corrente.

Regras automáticas de filtro por tenant devem ser implementadas em tarefas futuras.

## UUID

Entidades futuras usarão UUID como identificador.

Isso evita acoplamento a sequências globais e facilita integrações distribuídas.

## Timestamps e exclusão lógica

Mixins técnicos padronizam:

- criação.
- atualização.
- exclusão lógica.
- auditoria básica.

## Alembic

Alembic controla a evolução do schema.

A DEV-004 criou uma migration técnica inicial, sem entidades de negócio.

## Testes

Testes unitários validam mixins, convenção de nomes e contexto de tenant.

Testes de integração validam conexão real com PostgreSQL.

Esta aula não implementa regras de negócio do ERP.
