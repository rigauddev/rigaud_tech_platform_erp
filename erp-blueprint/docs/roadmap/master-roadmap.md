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

## Fase 2 — Core Inventory E Inbound Logistics

Objetivo: concluir o fluxo compartilhado de estoque antes das operações de restaurante e varejo.

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
- Deployment & Distribution Architecture.
- Product Documentation, Help Center & Knowledge Architecture.
- Put Away.
- Inventory Transactions.
- Inventory Count.
- Stock Adjustments.
- Transfers.

## Fase 3 — MVP Restaurante

Objetivo: construir o fluxo operacional inicial de restaurante sobre o Core compartilhado.

Sequência:

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

Experiencias ainda planejadas sobre essa base: gestao responsiva do restaurante, app operacional de garcom, KDS, app/portal do cliente por QR Code, PDV e entrada fiscal por NF-e/XML. Nenhuma delas esta implementada nesta fase de estoque.

## Fase 4 — MVP Loja de Roupas

Objetivo: reutilizar o Core e especializar o domínio Fashion.

Sequência:

- Produtos e variações.
- Categorias.
- Estoque compartilhado.
- Clientes.
- Pré-venda.
- Venda.
- Caixa.
- Cupom.
- NFC-e.

## Fase 5 — Evoluções Futuras

### EPIC-RESTAURANT-PRODUCTION

- Recipe Engine.
- Production Planning.
- Daily Production.
- Kitchen Production.
- Consumption.
- Waste.
- Forecast.
- AI Insights.

Produção permanece separada do estoque. Estoque registra consumo e perdas por eventos de `InventoryMovement`; receitas, planejamento e cozinha pertencem ao domínio Restaurant Production.

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
