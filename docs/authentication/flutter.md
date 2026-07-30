# Flutter Authentication

## Estrutura

- `features/auth/domain`: contratos, tokens, usuário autenticado e use case de login.
- `features/auth/data`: datasource remoto e implementação do repository.
- `features/auth/presentation`: login screen e controller Riverpod.
- `core/api`: Dio com Bearer token e tentativa de refresh.
- `core/storage`: storage seguro para access token e refresh token.

## Fluxo

1. Login envia `tenant`, `email` e `password`.
2. Tokens são salvos no storage seguro.
3. `/me` carrega o usuário autenticado.
4. Rotas protegidas usam `RouteGuard`.
5. Requests recebem `Authorization: Bearer`.
6. Em `401`, o interceptor tenta refresh uma vez e repete a request.
7. Logout revoga refresh token e limpa o storage.

## Contexto Ativo

Na DEV-010, a feature Auth passa a incluir modelos e repository para:

- consultar opções de contexto;
- trocar contexto ativo;
- salvar o novo access token retornado pela API;
- recarregar `/me` após a troca.

Não há tela final de seleção de empresa/filial nesta task.
