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

`GET /api/v1/auth/context` retorna apenas memberships e filiais ativos.

## JWT

O access token pode conter:

- `tenant_id`
- `membership_id`
- `branch_id`
- `branch_membership_id`
- `role`
- `access_scope`

O refresh token continua opaco.

Durante refresh, o backend revalida membership, filial, escopo e status no banco antes de emitir um novo access token com contexto.

Tokens com contexto antigo deixam de renovar se o membership ou a filial forem desativados.

## Compatibilidade

`auth_users.tenant_id` permanece como tenant base do usuário para compatibilidade com a fundação anterior.

Quando o JWT possui claims de contexto, o tenant ativo é aceito somente se existir `CompanyMembership` ativo para o usuário.

O backend continua sendo a fonte de verdade. O Flutter não grava tenant ou filial como autoridade independente do token.

## Isolamento

`BranchMembership` precisa apontar para uma filial do mesmo tenant do `CompanyMembership`.

Não é permitido associar membership da Empresa A a filial da Empresa B.

`branch_id = null` não significa acesso global. Acesso sem filial ativa só é aceito com `access_scope = all_branches`.

## Fora do Escopo

Não há autenticação nova, planos, cobrança, limites comerciais ou regras do restaurante nesta task.
