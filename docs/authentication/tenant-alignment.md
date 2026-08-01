# Authentication & Tenant Alignment

DEV-012 congela o contrato de autenticação antes da continuidade comercial.

## Decisões

- Login usa somente email e senha.
- O backend resolve `tenant_id`, `branch_id` e `role`.
- Um usuário pertence a exatamente uma empresa.
- Um usuário possui exatamente uma filial ativa.
- Usuário comum não troca filial.
- Troca de filial exige gestor, administrador ou permissão explícita.
- `tenant_id` permanece obrigatório em tabelas SaaS e On-Premise.

## JWT

O access token deve carregar:

- `sub` como `user_id`.
- `tenant_id`.
- `branch_id`.
- `role`.

Claims de membership podem permanecer durante a transição, mas não são a fonte oficial da decisão de tenant.

## Banco

A migration `0011_auth_tenant_alignment` prepara:

- `auth_users.active_branch_id`.
- `auth_users.role`.
- `auth_users.permissions`.
- `user_branch_history`.
- `user_work_assignments`.

As tabelas de membership existentes permanecem como compatibilidade técnica até uma task específica de RBAC/perfis.

## Frontend

A tela de login não exibe nem envia tenant. Qualquer seleção futura de filial deve ser uma operação autorizada e auditada após autenticação.
