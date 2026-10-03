# Rigaud Tech Platform ERP

O Rigaud Tech Platform ERP e uma plataforma ERP modular, multi-tenant e multiplataforma para pequenas e medias empresas.

## Objetivo

Organizar operacao, dados, historico, indicadores e automacoes em uma unica base evolutiva.

```text
Operacao
  ↓
Dados
  ↓
Historico
  ↓
Analytics
  ↓
Insights
  ↓
Automacao
  ↓
AI
```

## Modulos

- Gestao Empresarial;
- Produtos;
- Categorias;
- Estoque;
- Warehouse;
- Restaurante;
- Financeiro;
- Recursos Humanos;
- Producao;
- Analytics;
- AI/MCP;
- Administracao.

Alguns modulos estao implementados, outros estao em desenvolvimento ou planejados. O mapa oficial esta em `docs/architecture/product-map.md`.

O contrato documental do Restaurant Operations Core está em `docs/restaurant/README.md`.

## Arquitetura

- Multi-tenant;
- Multi-filial;
- SaaS;
- On-Premise;
- Hybrid;
- Offline-first planejado;
- API versionada;
- envelope padrao;
- auditoria;
- RBAC;
- Docs-as-Code;
- Academy;
- Help Center futuro;
- AI/MCP futuro.

## Ambientes

- Cloud compartilhado;
- Cloud dedicado futuro;
- On-Premise;
- Hybrid;
- desenvolvimento local com Docker.

## Documentacao

Esta pasta organiza documentacao tecnica, arquitetura, governanca, modulos, deployment, ajuda e conhecimento de produto.

O blueprint MkDocs fica em `erp-blueprint/docs`.

## Ajuda

A arquitetura da Central de Ajuda esta em `docs/help/README.md`.

Ela separa:

- documentacao tecnica;
- documentacao do usuario;
- Help Center;
- Academy;
- materiais comerciais futuros.

## Desenvolvimento

Antes de qualquer task, consultar:

- `AGENTS.md`;
- `erp-blueprint/MASTER_DEVELOPMENT_PROMPT.md`;
- `AI_DEVELOPMENT_CHARTER.md`;
- `ERP_DECISIONS.md`;
- `ERP_GLOSSARY.md`;
- `erp-blueprint/docs/backlog/task-registry.yaml`.

## Implantacao

Deployment e distribuicao estao documentados em:

- `docs/architecture/deployment/README.md`;
- `docs/deployment/README.md`.

## Roadmap

Roadmap oficial:

- `erp-blueprint/docs/roadmap/master-roadmap.md`;
- `erp-blueprint/docs/backlog/master-backlog.md`.
