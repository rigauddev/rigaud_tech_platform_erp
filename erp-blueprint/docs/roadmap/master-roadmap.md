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

Estado atual: concluído até DEV-010.

Próxima task prevista: DEV-011 — Assinaturas, Planos e Limites.

## Fase 2 — MVP Restaurante

Objetivo: construir o fluxo operacional inicial de restaurante usando o Core compartilhado.

Sequência:

- Produtos.
- Tenant, memberships, filiais e contexto ativo.
- Assinaturas, planos e limites.
- Categorias.
- Estoque.
- Mesas.
- Setores.
- Garçons.
- QR Code.
- Cardápio Online.
- Pedido Cliente.
- Pedido Garçom.
- KDS.
- Delivery.
- Caixa.
- Fechamento da Venda.
- Cupom ou NFC-e.

## EPIC-03 — Plataforma SaaS

Objetivo: manter planos, assinaturas, entitlements, feature flags e billing desacoplados dos módulos de negócio.

Sequência inicial:

- DEV-011 — SaaS Foundation.
- DEV-012 — Integração de limites e bloqueios comerciais.
- DEV-013 — Billing provider real e webhooks.

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

- Marketplace.
- Offline-first.
- Armazenamento externo de backups.
- WAL e Point-in-Time Recovery.
- Permissões avançadas.
- Planos e cobrança SaaS.
