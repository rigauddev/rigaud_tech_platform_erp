# Users

Feature Flutter de Usuários da Rigaud Tech Platform ERP.

## Estrutura

- `domain`: modelos, inputs, repository contract e use cases.
- `data`: datasource Dio e repository implementation.
- `presentation`: controllers Riverpod e telas.

## Telas

- Lista administrativa de usuários.
- Cadastro de usuário.
- Edição de usuário.
- Detalhe de usuário.
- Perfil atual.
- Troca de senha própria.
- Reset administrativo de senha.

Administração usa autorização temporária por `isSuperuser`.
