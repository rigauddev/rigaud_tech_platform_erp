# ADR 0001: Database Tenancy Strategy

## Status

Accepted

## Context

A Rigaud Tech Platform ERP precisa suportar SaaS e instalações on-premises sem criar um banco PostgreSQL por computador do usuário.

## Decision

Adotar:

- PostgreSQL compartilhado.
- Schema compartilhado.
- Isolamento lógico por `tenant_id`.
- Servidor PostgreSQL único por instalação on-premises.
- Nenhum PostgreSQL individual por computador.
- SQLite local somente em futura estratégia offline-first.

## Consequences

Entidades pertencentes a uma empresa deverão carregar `tenant_id`.

Entidades globais não serão obrigadas a carregar `tenant_id`.

A aplicação desktop no modo SaaS consumirá a API central e não terá PostgreSQL próprio.

Filtros automáticos, autenticação e resolução de tenant por JWT serão definidos em tasks futuras.
