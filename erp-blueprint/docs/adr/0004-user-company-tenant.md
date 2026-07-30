# ADR 0004: User como Identidade Autenticável da Empresa

## Status

Aceita.

## Contexto

A DEV-005 criou `auth_users` como fundação de autenticação.
A DEV-006 definiu `Company` como raiz oficial do tenant.
A DEV-007 precisa introduzir usuários funcionais sem duplicar identidade.

## Decisão

O usuário funcional do ERP é o registro existente em `auth_users`.

`auth_users.tenant_id` referencia `companies.id`.

Não será criada uma tabela `users` concorrente nesta etapa.

`status` é a fonte funcional de verdade para acesso:

- `active`
- `inactive`
- `blocked`

`is_active` permanece por compatibilidade e acompanha o status.

## Consequências

- Login e gestão de usuários usam a mesma identidade.
- Email permanece único por empresa.
- O mesmo email pode existir em empresas diferentes.
- Futuro RBAC deve se conectar ao usuário existente.
- Migrações futuras devem evoluir `auth_users` com cuidado para preservar sessões e autenticação.
