# Users Overview

A DEV-007 cria a fundação técnica de usuários multi-tenant.

O usuário oficial da plataforma é o registro autenticável em `auth_users`.
O módulo Users não cria uma tabela concorrente; ele evolui `auth_users` com dados de perfil, status funcional e operações administrativas.

## Objetivos

- Usuários pertencem a empresas.
- Email é único por empresa.
- Administração temporária usa `is_superuser`.
- Usuário comum acessa perfil próprio.
- Senhas podem ser trocadas ou resetadas.
- Sessões são revogadas em bloqueio, desativação e mudança de senha.

## Documentos

- `docs/users/backend.md`
- `docs/users/flutter.md`
- `docs/users/database.md`
- `docs/users/multi-tenancy.md`
- `docs/users/security.md`
- `docs/users/testing.md`
- `docs/users/troubleshooting.md`
