# Master Roadmap

Roadmap oficial da Rigaud Tech Platform ERP.

## Fase 1 — Fundação

- Workspace.
- Blueprint.
- Plataforma.
- Docker.
- Backend Starter.
- Flutter Starter.
- Banco de Dados Core.
- Autenticação.
- Empresas.
- Usuários.
- Governança, auditoria e respostas da API.
- Autenticação em dois fatores.
- Tenant, memberships, filiais e contexto ativo.
- Alinhamento Auth/Tenant: usuário com empresa única e filial ativa única.

Estado atual: concluído até DEV-012 em review.

Próxima task prevista: DEV-011 — Assinaturas, Planos e Limites.

DOC-008 congela a arquitetura de distribuicao: Cloud, Cloud Dedicated, On-Premise e Hybrid.

## Fase 2 — MVP Restaurante

Objetivo: construir o fluxo operacional inicial de restaurante usando o Core compartilhado.

Suporte transversal:

- Demo Environment para desenvolvimento, QA e demonstrações.
- Inventory Engine Domain antes da implementação REST-003.
- Deployment & Distribution Architecture antes de ampliar distribuicao Cloud/On-Premise/Hybrid.
- Product Documentation, Help Center & Knowledge Architecture antes de ampliar funcionalidades operacionais.

Engines planejadas:

- ENGINE-001 — Inventory Engine.
- ENGINE-002 — Order Engine.
- ENGINE-003 — Restaurant Engine.
- ENGINE-004 — POS Engine.
- ENGINE-005 — Financial Engine.
- ENGINE-006 — Reporting Engine.

Sequência:

- Produtos.
- Tenant, memberships, filiais e contexto ativo.
- Assinaturas, planos e limites.
- Categorias de Produtos.
- Alinhamento Auth/Tenant.
- Inventory Engine.
- Warehouse Management.
- Warehouse Zones.
- Warehouse Locations.
- Receiving Documents.
- Goods Receipt.
- Product Documentation, Help Center & Knowledge Architecture.
- Put Away.
- Inventory Transactions.
- Inventory Count.
- Stock Adjustments.
- Transfers.
- Mesas.
- Setores.
- Garçons.
- QR Code.
- Cardápio Online.
- Pedidos.
- KDS.
- Delivery.
- Caixa.
- Cupom ou NFC-e.

## Fase 3 — MVP Loja de Roupas

Objetivo: reutilizar o Core e especializar o domínio Fashion.

Sequência:

- Produtos e variações.
- Categorias.
- Estoque.
- Clientes.
- Pré-venda.
- Venda.
- Caixa.
- Cupom.
- NFC-e.

## Fase 4 — Evoluções Futuras

- Financial MVP.
- HR MVP com Employees, Departments, Shifts, Schedules, Vacation e Attendance.
- Production MVP, com cliente real aguardando esta capacidade.
- AI/MCP incremental.
- Marketplace.
- Offline-first.
- Armazenamento externo de backups.
- WAL e Point-in-Time Recovery.
- Permissões avançadas.
- Planos e cobrança SaaS.
