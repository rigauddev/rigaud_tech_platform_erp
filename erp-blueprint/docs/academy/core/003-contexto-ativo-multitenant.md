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

## Revalidação

Claims ajudam o backend a carregar o contexto, mas não substituem o banco.

Ao consultar usuário atual ou renovar sessão, o backend deve revalidar membership, filial e escopo.

Se um vínculo for desativado, novos tokens não devem preservar aquele contexto.

## IDOR

Troca de contexto nunca deve confiar em UUID enviado pelo cliente.

O tenant solicitado precisa pertencer ao usuário por `CompanyMembership`.

A filial solicitada precisa pertencer ao mesmo tenant e ao usuário por `BranchMembership`.

## Limite da Task

Esta aula não cobre estoque, venda, assinatura, cobrança ou permissões avançadas.
