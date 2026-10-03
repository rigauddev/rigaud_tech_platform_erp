# Master Backlog

Backlog oficial e congelado da Rigaud Tech Platform ERP.

## EPIC-0001 — Fundação

Ordem congelada:

1. ARCH-001 — Workspace
2. ARCH-002 — Blueprint
3. ARCH-003 — Platform
4. DEV-001 — Docker
5. DEV-002 — Backend Starter
6. DEV-003 — Flutter Starter
7. DEV-004 — Banco de Dados
8. DEV-005 — Autenticação
9. DEV-006 — Empresas
10. DEV-007 — Usuários
11. DEV-008 — Governança, Auditoria e Respostas da API
12. DEV-009 — Autenticação em Dois Fatores
13. DEV-010 — Tenant, Memberships, Filiais e Contexto Ativo
14. DEV-012 — Authentication & Tenant Architecture Alignment

Estado atual:

- ARCH-001 — concluída.
- ARCH-002 — concluída.
- ARCH-003 — concluída.
- DEV-001 — concluída.
- DEV-002 — concluída.
- DEV-003 — concluída.
- DEV-004 — concluída.
- DEV-005 — concluída.
- DEV-006 — concluída.
- DEV-007 — concluída.
- DEV-008 — concluída.
- DEV-009 — concluída.
- DEV-010 — concluída.
- DEV-012 — em review.

Próxima task prevista:

```text
DEV-011 — Assinaturas, Planos e Limites
```

DEV-009 deverá permitir autenticação em dois fatores habilitável e desabilitável por email, telefone e aplicativo autenticador.

DEV-012 congela a regra oficial: usuário pertence a uma empresa e possui uma filial ativa.

UI-002 — Navigation & Application Shell permanece como refinamento transversal em review. Ela não altera a ordem das tasks comerciais.

UI-003 — Navigation Access & Login Brand Fix permanece como correção transversal em review. Ela não amplia a matriz de permissões de negócio e não altera a sequência comercial.

UI-004 — Localization & Login Flow permanece como refinamento transversal em review. Traduções completas e recuperação de senha por email dependem de tasks dedicadas; cada tela alterada deve manter um único idioma por vez.

## Core Inventory E Inbound Logistics

Tasks transversais de suporte:

- DOC-003 — Demo Environment.
- DOC-005 — Inventory Engine Domain.
- DOC-008 — Deployment & Distribution Architecture.
- DOC-009 — Product Documentation, Help Center & Knowledge Architecture.

Estratégia Engine-first:

- ENGINE-001 — Inventory Engine.
- ENGINE-002 — Order Engine.
- ENGINE-003 — Restaurant Engine.
- ENGINE-004 — POS Engine.
- ENGINE-005 — Financial Engine.
- ENGINE-006 — Reporting Engine.

Sequência concluída/iniciada para o núcleo compartilhado:

1. REST-001 — Cadastro de Produtos
2. DEV-010 — Tenant, Memberships, Filiais e Contexto Ativo
3. DEV-011 — Assinaturas, Planos e Limites
4. REST-002 — Categorias de Produtos
5. DEV-012 — Authentication & Tenant Architecture Alignment
6. REST-003 — Inventory Engine
7. REST-004 — Warehouse Management
8. REST-005 — Warehouse Zones
9. REST-006 — Warehouse Locations
10. REST-007 — Receiving Documents
11. REST-008 — Goods Receipt
12. DOC-008 — Deployment & Distribution Architecture
13. DOC-009 — Product Documentation, Help Center & Knowledge Architecture
14. REST-009 — Put Away
15. REST-010 — Inventory Transactions
16. REST-011 — Inventory Count
17. REST-012 — Stock Adjustments
18. REST-013 — Transfers

Cada item é uma Task independente. A ordem não pode ser alterada.

## MVP Restaurante

Após concluir o núcleo de estoque e inbound logistics, iniciar o Restaurante nesta ordem:

1. Restaurant-001 — Mesas
2. Restaurant-002 — Setores
3. Restaurant-003 — Garçons
4. Restaurant-004 — Menu do Dia e Disponibilidade Comercial
5. Restaurant-005 — QR Code das Mesas
6. Restaurant-006 — Cardápio Online
7. Restaurant-007 — Pedidos, Garçom Responsável e Roteamento para Cozinha
8. Restaurant-008 — Kitchen Display — KDS e Impressão
9. Restaurant-009 — Delivery
10. Restaurant-010 — Caixa
11. Restaurant-011 — Cupom ou NFC-e

O Menu do Dia é publicado por filial e período de serviço. A quantidade vendável é uma cota comercial diária e não altera `InventoryBalance`; a integração automática com produção e insumos fica para a EPIC-RESTAURANT-PRODUCTION.

## EPIC-RESTAURANT-PRODUCTION — Futura

Não implementar antes do MVP Restaurante.

Escopo planejado:

- Recipe Engine;
- Production Planning;
- Daily Production;
- Kitchen Production;
- Consumption;
- Waste;
- Forecast;
- AI Insights.

Produção de restaurante consumirá insumos por `InventoryMovement` com `origin_module=RESTAURANT_PRODUCTION` e `business_process=PRODUCTION`.

## MVP Loja de Roupas

Após a conclusão do Restaurante, iniciar o módulo Fashion nesta ordem:

1. STORE-001 — Produtos e variações
2. STORE-002 — Categorias
3. STORE-003 — Estoque
4. STORE-004 — Clientes
5. STORE-005 — Pré-venda
6. STORE-006 — Venda
7. STORE-007 — Caixa
8. STORE-008 — Cupom
9. STORE-009 — NFC-e

A Loja deve reutilizar o máximo possível do Core.

## Prioridade Pos-MVP

1. Finalizar Inventory Engine.
2. Restaurant MVP.
3. Financial MVP.
4. HR MVP:
   - Employees;
   - Departments;
   - Shifts;
   - Schedules;
   - Vacation;
   - Attendance.
5. Production MVP.
6. AI/MCP incremental.

Existe cliente real aguardando Production MVP. Production Engine permanece independente do Restaurant.
