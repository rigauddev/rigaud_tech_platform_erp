# Rigaud Tech Platform ERP

Workspace base para iniciar o desenvolvimento da plataforma ERP da Rigaud Tech.

Este repositório contém apenas a estrutura inicial de pastas e documentação de orientação. Funcionalidades, código de negócio e implementações técnicas serão adicionados nas próximas etapas do projeto.

## Estrutura principal

- `erp-blueprint`: materiais de arquitetura, visão de produto e decisões técnicas.
- `erp-platform`: base da futura plataforma ERP.
- `scripts`: automações e utilitários de apoio ao projeto.
- `docs`: documentação geral do workspace.

## Status Atual

Fundação concluída até:

```text
DEV-010 — Tenant, Memberships, Filiais e Contexto Ativo
```

Task atual:

```text
DOC-006 — AI Development Charter, ERP Decisions e ERP Glossary
```

Antes de iniciar novas tasks, leia `erp-blueprint/MASTER_DEVELOPMENT_PROMPT.md`.

Fontes permanentes adicionais:

- `AI_DEVELOPMENT_CHARTER.md`
- `ERP_DECISIONS.md`
- `ERP_GLOSSARY.md`

## Desenvolvimento com Docker

A infraestrutura de desenvolvimento está configurada para subir toda a stack com um único comando:

```bash
make up
```

Comandos disponíveis:

- `make up`
- `make down`
- `make restart`
- `make logs`
- `make backend`
- `make flutter`
- `make shell-backend`
- `make shell-db`
- `make lint`
- `make format`
- `make test`
- `make demo`
- `make demo-users`
- `make demo-platform`
- `make demo-restaurant`
- `make demo-retail`
- `make demo-scenarios`
- `make demo-reset`
- `make playground`

Detalhes em `docs/development/docker.md`.

## Ambiente Demo

O ambiente demo oficial e o Scenario Engine estão documentados em `docs/demo/overview.md`.

Fluxo rápido:

```bash
make up
make demo
```

Contas disponíveis em `docs/demo/accounts.md`.

Na DOC-003, o seed cria dados para empresas, filiais, usuários, categorias e produtos. A API `/api/v1/demo/*` e o Dashboard Demo do Flutter existem apenas para desenvolvimento. Cenários completos de mesas, pedidos, estoque, clientes, QR Code e vendas permanecem documentados para evolução nas tasks comerciais futuras.

## Backend

A base inicial do backend está documentada em `docs/backend/backend-starter.md`.

A fundação técnica de banco está documentada em `docs/database/overview.md`.

A fundação de autenticação está documentada em `docs/authentication/overview.md`.

A fundação de empresas e tenant real está documentada em `docs/companies/overview.md`.

A fundação de usuários multi-tenant está documentada em `docs/users/overview.md`.

A fundação transversal de governança, auditoria, logs e respostas da API está documentada em `docs/governance/task-management.md`, `docs/observability/overview.md`, `docs/api/response-contract.md` e `docs/audit/overview.md`.

A autenticação em dois fatores está documentada em `docs/authentication/mfa-overview.md`.

O contexto ativo multi-empresa e multi-filial está documentado em `docs/authentication/context.md` e `docs/companies/multi-tenancy.md`.

O cadastro de produtos está documentado em `docs/products/overview.md`.

O cadastro de categorias está documentado em `docs/categories/overview.md`.

O ambiente demo está documentado em `docs/demo/overview.md`.

O domínio do Inventory Engine está documentado em `docs/inventory/overview.md`.

Endpoints técnicos disponíveis:

- `GET /health`
- `GET /api/v1/health`
- `GET /health/database`
- `GET /api/v1/health/database`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/auth/context`
- `POST /api/v1/auth/context/switch`
- `GET /api/v1/auth/mfa/status`
- `POST /api/v1/auth/mfa/totp/setup`
- `POST /api/v1/auth/mfa/totp/confirm`
- `POST /api/v1/auth/mfa/email/setup`
- `POST /api/v1/auth/mfa/email/confirm`
- `POST /api/v1/auth/mfa/sms/setup`
- `POST /api/v1/auth/mfa/sms/confirm`
- `POST /api/v1/auth/mfa/verify`
- `POST /api/v1/companies`
- `GET /api/v1/companies`
- `GET /api/v1/companies/current`
- `POST /api/v1/companies/branches`
- `GET /api/v1/companies/branches`
- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `POST /api/v1/users/me/change-password`
- `GET /api/v1/audit/events`
- `GET /api/v1/audit/events/{event_id}`
- `POST /api/v1/products`
- `GET /api/v1/products`
- `GET /api/v1/products/{product_id}`
- `PATCH /api/v1/products/{product_id}`
- `POST /api/v1/products/{product_id}/activate`
- `POST /api/v1/products/{product_id}/deactivate`
- `POST /api/v1/products/{product_id}/availability`
- `DELETE /api/v1/products/{product_id}`
- `POST /api/v1/categories`
- `GET /api/v1/categories`
- `GET /api/v1/categories/{category_id}`
- `PATCH /api/v1/categories/{category_id}`
- `POST /api/v1/categories/{category_id}/activate`
- `POST /api/v1/categories/{category_id}/deactivate`
- `POST /api/v1/categories/{category_id}/reorder`
- `DELETE /api/v1/categories/{category_id}`
- `GET /api/v1/demo/status`
- `GET /api/v1/demo/install`
- `GET /api/v1/demo/reset`
- `GET /api/v1/demo/scenarios`
- Swagger em `/docs`
- OpenAPI em `/openapi.json`

## Frontend

A base inicial do frontend Flutter está documentada em `docs/frontend/flutter-starter.md`.

Integração Flutter de autenticação documentada em `docs/authentication/flutter.md`.

Documentação complementar:

- `docs/frontend/project-structure.md`
- `docs/frontend/platforms.md`
- `docs/frontend/responsive-design.md`
# rigaud_tech_platform_erp
# rigaud_tech_platform_erp
