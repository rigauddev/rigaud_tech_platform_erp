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
- O wizard futuro separa servicos de deployment de modulos licenciados.
- A carencia offline e de ate 30 dias; depois, novas escritas param e leitura/exportacao permanecem.
- Revogacao remota assinada bloqueia todo acesso quando recebida, preservando banco e backups.
- Instalacao desconectada nao pode receber comandos remotos ate reconectar.
- Nao existe garantia absoluta contra copia ou modificacao de software em hardware administrado pelo cliente.
- AI/MCP futuro deve respeitar tenant, branch, role, permissions e audit.

O comportamento e os limites de seguranca estao detalhados na ADR 0010 e no
documento On-Premise Installation Wizard and Licensing.
