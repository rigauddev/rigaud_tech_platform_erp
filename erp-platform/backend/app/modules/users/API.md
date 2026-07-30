# Users API

Rotas expostas em `/api/v1/users`.

## Administração

- `POST /users`
- `GET /users`
- `GET /users/{user_id}`
- `PATCH /users/{user_id}`
- `POST /users/{user_id}/activate`
- `POST /users/{user_id}/deactivate`
- `POST /users/{user_id}/block`
- `POST /users/{user_id}/unblock`
- `POST /users/{user_id}/reset-password`

As rotas administrativas exigem usuário autenticado com `is_superuser=true`.

## Perfil Próprio

- `GET /users/me`
- `PATCH /users/me`
- `POST /users/me/change-password`

Usuários comuns podem editar apenas campos de perfil: nome, sobrenome, nome de exibição e telefone.
