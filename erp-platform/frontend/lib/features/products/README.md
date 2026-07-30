# Products

Feature responsável pelo cadastro de produtos.

Estrutura:

- `domain`: entidade, input, contrato de repositório e use cases.
- `data`: datasource remoto e implementação do repositório.
- `presentation`: controller Riverpod, listagem, formulário e detalhe.

A feature consome o envelope padrão da API e utiliza o tenant autenticado pelo backend.
