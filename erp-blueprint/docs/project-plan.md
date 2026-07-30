# Plano Oficial do Projeto

Este documento é a fonte oficial do direcionamento da Rigaud Tech Platform ERP.

## Produto

Nome oficial:

```text
Rigaud Tech Platform ERP
```

A Rigaud Tech Platform ERP é uma plataforma ERP modular, multi-tenant e multiplataforma.

A plataforma terá módulos compartilhados e módulos específicos por segmento.

## Stack Oficial

Backend:

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- Docker

Frontend:

- Flutter
- Android
- iOS
- Web
- Windows
- macOS

Arquitetura:

- Clean Architecture
- DDD simplificado
- Repository Pattern
- Use Case Pattern
- Dependency Injection
- Feature First no Flutter
- MVVM no Flutter
- Docs-as-Code

Estas tecnologias não devem ser substituídas sem decisão arquitetural formal futura.

## Estrutura Congelada

Workspace:

```text
workspace/
  erp-blueprint/
  erp-platform/
  scripts/
  docs/
```

Blueprint:

```text
erp-blueprint/
  README.md
  mkdocs.yml
  docs/
    academy/
    adr/
    architecture/
    backlog/
    checklists/
    diagrams/
    examples/
    glossary/
    journal/
    modules/
    prompts/
    research/
    roadmap/
    sprints/
    templates/
```

Platform:

```text
erp-platform/
  apps/
  backend/
  frontend/
  shared/
  packages/
  docker/
  database/
  scripts/
  tests/
  .github/
  docker-compose.yml
  Makefile
  .env.example
```

Estrutura base do backend:

```text
backend/
  app/
  core/
  modules/
  shared/
  tests/
  migrations/
```

Estrutura base do Flutter:

```text
frontend/
  lib/
    core/
    features/
    shared/
    config/
```

Não criar arquiteturas paralelas. Não mover ou renomear módulos estabelecidos sem necessidade comprovada.

## Módulos Planejados

- Rigaud Core
- Rigaud Restaurant
- Rigaud Fashion
- Rigaud Finance
- Rigaud Inventory
- Rigaud POS
- Rigaud Delivery
- Rigaud Fiscal
- Rigaud CRM
- Marketplace, futuro

## Estratégia de Produto

```text
Rigaud Core
    ↓
Módulos por segmento
    ↓
Fiscal isolado
```

O Core será reutilizado pelo Restaurante, Loja de Roupas e futuros segmentos.

Elementos compartilhados:

- Autenticação
- Empresas
- Usuários
- Produtos
- Categorias
- Estoque
- Clientes
- Vendas
- Caixa
- Financeiro
- Auditoria
- Autenticação em dois fatores
- Configurações

Elementos específicos do Restaurante:

- Mesas
- Setores
- Garçons
- Cardápio
- QR Code
- Pedidos
- KDS
- Delivery
- Taxa de serviço
- Divisão da conta

Elementos específicos da Loja de Roupas:

- Cor
- Tamanho
- Grade
- Coleção
- Marca
- Comissão
- Pré-venda
- Reserva de produtos

## Multi-Tenancy

SaaS:

```text
Flutter Web, Desktop ou Mobile
        ↓
FastAPI na nuvem
        ↓
PostgreSQL compartilhado
        ↓
tenant_id
```

A versão Desktop não possui PostgreSQL individual quando estiver usando o SaaS.

Windows, macOS e Linux funcionam como clientes da mesma API.

On-premises:

```text
Dispositivos da empresa
        ↓
Rede local
        ↓
FastAPI local
        ↓
PostgreSQL local único
```

Em uma instalação local deverá existir apenas um servidor PostgreSQL para a empresa.

Não instalar banco independente em cada computador.

Offline-first futuro:

```text
Flutter
    ↓
SQLite local
    ↓
Fila de sincronização
    ↓
FastAPI
    ↓
PostgreSQL
```

O modo offline-first não pertence ao MVP atual.

## Backup

Para instalações locais e ambientes de produção:

- Backup diário.
- Backup antes de atualização.
- Backup manual.
- Cópia local.
- Cópia externa futura.
- Teste periódico de restauração.

Não executar backup completo a cada alteração de registro.

Volumes Docker não substituem backup.

Evoluções futuras poderão usar WAL, Point-in-Time Recovery e armazenamento externo como Amazon S3.

Esses recursos não devem ser implementados fora da Task correspondente.

## Fiscal

O módulo fiscal é isolado.

A venda nunca dependerá obrigatoriamente da emissão fiscal para ser concluída.

Fluxo definido:

```text
Finalizar venda
      ↓
Escolher documento

( ) Cupom
( ) NFC-e
```

A venda é concluída mesmo quando a NFC-e não estiver habilitada.

No MVP inicial, o fiscal deve ser apenas preparado.

Não acoplar regras fiscais diretamente ao módulo de vendas.

## Estado Atual

- ARCH-001: concluída.
- ARCH-002: concluída.
- ARCH-003: concluída.
- DEV-001: concluída.
- DEV-002: concluída.
- DEV-003: concluída.
- DEV-004: concluída.
- DEV-005: concluída.
- DEV-006: concluída.
- DEV-007: concluída.
- DEV-008: concluída.

Próxima Task oficial:

```text
DEV-009 — Autenticação em Dois Fatores
```

Não marcar uma Task como concluída sem evidência no repositório.

## Divergências Registradas

- Antes deste alinhamento não havia `AGENTS.md` no workspace.
- `erp-blueprint/docs/backlog/README.md` e `erp-blueprint/docs/roadmap/README.md` estavam vazios de conteúdo funcional.
- `erp-blueprint/docs/adr/README.md` dizia que nenhuma ADR existia, mas já havia ADR 0001 e ADR 0002.
