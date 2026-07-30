# Companies Multi-Tenancy

`Company` é a raiz do tenant.

Fluxo:

```text
slug ou código da empresa
        ↓
CompanyRepository
        ↓
Company ativa
        ↓
company.id
        ↓
tenant_id
```

Regras:

- Não confiar em UUID arbitrário recebido do frontend.
- Resolver empresa por slug ou código.
- Empresa inativa bloqueia novos logins.
- Empresa suspensa bloqueia novos logins.
- Tokens já emitidos seguem a política da autenticação.
- Futuras entidades usarão `tenant_id = company.id`.
- Filiais usam `tenant_id` e não substituem a raiz do tenant.
- Produtos continuam tenant-wide e não recebem `branch_id`.
- Entidades operacionais futuras, como estoque e movimentações, poderão exigir `branch_id`.
- Token sem `branch_id` só é válido para usuários com `access_scope = all_branches`.

O campo temporário `auth_users.tenant_slug` foi preservado por compatibilidade, mas a resolução oficial do tenant usa `companies`.

## Contexto Ativo

O contexto ativo define em qual empresa e filial o usuário está operando.

Claims preparadas no JWT:

- `tenant_id`
- `membership_id`
- `branch_id`
- `branch_membership_id`
- `role`
- `access_scope`

`CompanyMembership` define o vínculo do usuário com a empresa.

`BranchMembership` define o vínculo do usuário com uma filial específica.

Usuários com `access_scope = selected_branches` precisam operar com `branch_id`.

Usuários com `access_scope = all_branches` podem operar sem filial ativa quando a operação permitir visão consolidada.
