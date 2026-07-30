# Companies

Feature administrativa de empresas.

Estrutura:

- `data`: datasource remoto e repository implementation.
- `domain`: Company, input, contratos e use cases.
- `presentation`: controller Riverpod, lista, formulário e detalhes.

Rotas administrativas exigem superuser.

Usuário comum consulta somente a empresa atual.
