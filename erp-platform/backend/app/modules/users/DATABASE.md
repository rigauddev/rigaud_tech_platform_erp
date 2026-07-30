# Users Database

O módulo Users utiliza a tabela `auth_users`.

Não foi criada uma tabela `users` separada para evitar duplicidade de identidade.

## Campos Técnicos

- `tenant_id`
- `email`
- `password_hash`
- `first_name`
- `last_name`
- `display_name`
- `phone`
- `status`
- `is_active`
- `is_superuser`
- `must_change_password`
- `failed_login_attempts`
- `locked_until`
- `last_login_at`
- `created_at`
- `updated_at`
- `deleted_at`
- `created_by`
- `updated_by`
- `deleted_by`

`tenant_id` aponta para `companies.id`.
