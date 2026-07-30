# Token Strategy

## Access Token

JWT assinado com `HS256`.

Claims obrigatórias:

- `sub`
- `tenant_id`
- `token_type`
- `iat`
- `exp`
- `jti`

`token_type` deve ser `access`.

Claims opcionais de contexto ativo:

- `membership_id`
- `branch_id`
- `branch_membership_id`
- `role`
- `access_scope`

Quando `branch_id` não estiver presente, a operação só deve aceitar o token se o usuário possuir `access_scope = all_branches`.

## Refresh Token

Refresh token é opaco, aleatório e não é JWT.

No banco, apenas o hash SHA-256 do refresh token é persistido.

Cada refresh válido gera uma nova sessão e revoga a sessão anterior. Reuso de refresh token revogado é tratado como token inválido e registrado em auditoria.

Na DEV-010, a sessão pode preservar contexto ativo para emissão do access token durante refresh.
