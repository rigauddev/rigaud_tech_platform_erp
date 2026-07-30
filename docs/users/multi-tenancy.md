# Users Multi-Tenancy

Usuários pertencem a empresas.

```text
auth_users.tenant_id = companies.id
```

## Email

O email é normalizado em lowercase e único dentro da empresa.

O mesmo email pode existir em empresas diferentes.

## Tenant

O frontend não escolhe tenant para autenticação.
Login continua usando `tenant`, `email` e `password`.
O backend resolve o tenant pela empresa.
