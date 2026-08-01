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

Cada usuário pertence a uma única empresa/tenant e possui uma única filial ativa.

O login não recebe tenant. O backend encontra o usuário por email, valida a empresa ativa e emite JWT com tenant, filial ativa e papel.

`status` é a fonte funcional de verdade para acesso:

- `active`
- `inactive`
- `blocked`

`is_active` permanece por compatibilidade e acompanha o status.

## Consequências

- Login e gestão de usuários usam a mesma identidade.
- Email autenticável é único globalmente.
- O mesmo email não pode existir em empresas diferentes enquanto não houver uma task específica de usuário multiempresa.
- Troca de filial deve gerar histórico em `user_branch_history`.
- Lotação atual deve ser representável em `user_work_assignments`.
- Futuro RBAC deve se conectar ao usuário existente.
- Migrações futuras devem evoluir `auth_users` com cuidado para preservar sessões e autenticação.
