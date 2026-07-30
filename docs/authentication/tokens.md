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

## Refresh Token

Refresh token é opaco, aleatório e não é JWT.

No banco, apenas o hash SHA-256 do refresh token é persistido.

Cada refresh válido gera uma nova sessão e revoga a sessão anterior. Reuso de refresh token revogado é tratado como token inválido e registrado em auditoria.
