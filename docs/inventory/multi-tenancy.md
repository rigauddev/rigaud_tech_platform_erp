# Multi-Tenant E Multi-Filial

## Tenant

O Inventory Engine usa `tenant_id = companies.id`.

Toda tabela operacional planejada deve possuir `tenant_id`.

## Filial

Estoque é operacionalmente filializado.

Toda operação que altera disponibilidade deve possuir `branch_id`.

## Warehouse

Warehouse pertence a uma filial.

Transferências entre filiais são permitidas dentro do mesmo tenant.

Transferências entre tenants são proibidas.

## Isolamento

Regras:

- nenhuma consulta deve retornar dados de outro tenant;
- filtros por tenant são obrigatórios em repositórios;
- filtros por filial dependem do contexto ativo do usuário;
- usuários com `all_branches` podem consultar múltiplas filiais do mesmo tenant;
- usuários com `selected_branches` ficam restritos às filiais autorizadas.

