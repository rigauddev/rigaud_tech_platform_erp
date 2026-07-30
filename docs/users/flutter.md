# Users Flutter

Feature em `erp-platform/frontend/lib/features/users`.

## Organização

- `data`: Dio datasource e repository implementation.
- `domain`: modelos, inputs, repository contract e use cases.
- `presentation`: controllers Riverpod e telas.

## Rotas

- `/users`
- `/users/new`
- `/users/me`
- `/users/me/change-password`
- `/users/:userId`
- `/users/:userId/edit`
- `/users/:userId/reset-password`

Usuários comuns são redirecionados para `/users/me` ao tentar acessar rotas administrativas.
