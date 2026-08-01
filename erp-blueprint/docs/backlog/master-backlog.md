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

Próxima task prevista:

```text
DEV-011 — Assinaturas, Planos e Limites
```

DEV-009 deverá permitir autenticação em dois fatores habilitável e desabilitável por email, telefone e aplicativo autenticador.

DEV-010 prepara contexto ativo multi-empresa e multi-filial antes das regras comerciais dependentes de filial.

## MVP Restaurante

Task transversal de suporte antes da continuidade operacional:

- DOC-003 — Demo Environment.
- DOC-005 — Inventory Engine Domain.

Estratégia Engine-first:

- ENGINE-001 — Inventory Engine.
- ENGINE-002 — Order Engine.
- ENGINE-003 — Restaurant Engine.
- ENGINE-004 — POS Engine.
- ENGINE-005 — Financial Engine.
- ENGINE-006 — Reporting Engine.

Após DEV-009, executar exatamente nesta ordem:

1. REST-001 — Cadastro de Produtos
2. DEV-010 — Tenant, Memberships, Filiais e Contexto Ativo
3. DEV-011 — Assinaturas, Planos e Limites
4. REST-002 — Categorias de Produtos
5. REST-003 — Controle de Estoque
6. REST-004 — Mesas
7. REST-005 — Setores
8. REST-006 — Garçons
9. REST-007 — QR Code das Mesas
10. REST-008 — Cardápio Online
11. REST-009 — Pedido pelo Cliente
12. REST-010 — Pedido pelo Garçom
13. REST-011 — Painel da Cozinha — KDS
14. REST-012 — Delivery
15. REST-013 — Caixa
16. REST-014 — Fechamento da Venda
17. REST-015 — Cupom ou NFC-e

Cada item é uma Task independente. A ordem não pode ser alterada.

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
