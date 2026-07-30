# Database Overview

A Rigaud Tech Platform ERP usa PostgreSQL 16 como banco relacional principal.

## Arquitetura

- PostgreSQL compartilhado.
- Schema compartilhado.
- Isolamento lógico por `tenant_id` em entidades pertencentes a uma empresa.
- SQLAlchemy 2.x assíncrono no backend.
- Alembic para evolução controlada do schema.

## SaaS e on-premises

No modo SaaS, o aplicativo desktop ou web não possui PostgreSQL próprio. Ele acessa a API central, e a API persiste dados no PostgreSQL compartilhado.

Em instalação on-premises, a arquitetura prevista é um servidor PostgreSQL único por instalação, não um banco individual por computador.

SQLite local fica reservado para uma estratégia futura offline-first, ainda não implementada.

## Persistência e backup

Volume Docker preserva dados entre reinícios de containers, mas não substitui backup.

Backup exige cópia externa verificável e restauração testada periodicamente.
