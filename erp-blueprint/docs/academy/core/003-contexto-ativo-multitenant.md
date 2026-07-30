# Contexto Ativo Multi-Tenant

DEV-010 introduz a fundação de contexto ativo da Rigaud Tech Platform ERP.

## Ideia Central

`Company` continua sendo a raiz do tenant.

`Branch` representa uma filial, loja, unidade ou matriz dentro da empresa.

O usuário não acessa uma empresa diretamente apenas por existir no banco. Ele precisa de um `CompanyMembership`.

Para operar em uma filial específica, ele também precisa de um `BranchMembership`.

## Token

O JWT passa a carregar contexto técnico opcional:

- empresa ativa;
- membership de empresa;
- filial ativa;
- membership de filial;
- papel;
- escopo de acesso.

Isso permite que futuras features validem isolamento por tenant e por filial sem duplicar lógica.

## Limite da Task

Esta aula não cobre estoque, venda, assinatura, cobrança ou permissões avançadas.
