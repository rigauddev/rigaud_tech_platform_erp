# Companies Flutter

## Estrutura

- `features/companies/domain`: modelo, input, repository e use cases.
- `features/companies/data`: datasource remoto e repository implementation.
- `features/companies/presentation`: controller Riverpod, lista, formulário e detalhes.

## Telas

- Lista de empresas.
- Cadastro de empresa.
- Edição de empresa.
- Detalhes da empresa.
- Minha empresa.

Rotas administrativas exigem superuser no `RouteGuard`.

Usuário comum é redirecionado para `/companies/current`.
