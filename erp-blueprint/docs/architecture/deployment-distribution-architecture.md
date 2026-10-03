# Deployment & Distribution Architecture

DOC-008 congela a arquitetura oficial de deployment e distribuicao.

Documentacao operacional no workspace:

- `docs/architecture/deployment/README.md`;
- `docs/architecture/system-map.md`;
- `docs/architecture/offline-strategy.md`;
- `docs/architecture/cloud.md`;
- `docs/architecture/on-premise.md`;
- `docs/architecture/hybrid.md`;
- `docs/architecture/resellers.md`.

## Decisoes

- Tenant e `Company`.
- Deployment e o ambiente tecnico.
- Tipos oficiais: `CLOUD_SHARED`, `CLOUD_DEDICATED`, `ON_PREMISE` e `HYBRID`.
- Partner/Reseller nao e tenant.
- On-Premise continua sendo o mesmo ERP.
- Servidor On-Premise recomendado em producao: Linux.
- AI/MCP futuro deve respeitar tenant, branch, role, permissions e audit.
