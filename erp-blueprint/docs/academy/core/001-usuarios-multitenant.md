# Academy: Usuários Multi-Tenant

## Objetivo

Explicar a base técnica de usuários multi-tenant da Rigaud Tech Platform ERP.

## Modelo Mental

Empresa é o tenant.
Usuário pertence a uma empresa.

```text
Company.id
  ↓
auth_users.tenant_id
```

## Por que não criar outra tabela users?

Porque `auth_users` já é a identidade autenticável.
Criar outra tabela agora geraria duplicidade entre login e perfil funcional.

## Status do Usuário

`status` define se o usuário pode acessar:

- `active`: acesso permitido.
- `inactive`: acesso negado.
- `blocked`: acesso negado.

`is_active` continua existindo para compatibilidade.

## Sessões

Quando um usuário é desativado, bloqueado ou troca senha, sessões ativas são revogadas.
Isso força novo login e reduz risco de uso indevido de tokens antigos.
