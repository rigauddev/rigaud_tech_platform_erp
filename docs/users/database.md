# Users Database

A migration `0005_users` evolui a tabela `auth_users`.

## Decisão

Não existe tabela `users` separada.
O mesmo registro usado para autenticação passa a representar o usuário funcional do ERP.

## Status

`status` é a fonte de verdade:

- `active`: usuário pode autenticar.
- `inactive`: usuário não pode autenticar.
- `blocked`: usuário não pode autenticar.

`is_active` é mantido como campo de compatibilidade derivado.
