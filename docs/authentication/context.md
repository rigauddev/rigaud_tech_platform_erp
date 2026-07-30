# Active Context

DEV-010 prepara a autenticação para operar em múltiplas empresas e múltiplas filiais.

## Conceitos

- `tenant_id`: identifica a empresa raiz.
- `membership_id`: vínculo do usuário com a empresa.
- `branch_id`: filial ativa, quando selecionada.
- `branch_membership_id`: vínculo do usuário com a filial.
- `role`: papel técnico no contexto ativo.
- `access_scope`: define se o usuário opera em todas as filiais ou apenas nas filiais selecionadas.

## Endpoints

- `GET /api/v1/auth/context`
- `POST /api/v1/auth/context/switch`

`GET /api/v1/auth/context` retorna o contexto ativo e as opções de empresa/filial disponíveis para o usuário autenticado.

`POST /api/v1/auth/context/switch` valida se o usuário pode operar no tenant e na filial informados e retorna um novo access token.

## JWT

O access token pode conter:

- `tenant_id`
- `membership_id`
- `branch_id`
- `branch_membership_id`
- `role`
- `access_scope`

O refresh token continua opaco.

## Fora do Escopo

Não há autenticação nova, planos, cobrança, limites comerciais ou regras do restaurante nesta task.
