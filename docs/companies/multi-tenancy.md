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

O campo temporário `auth_users.tenant_slug` foi preservado por compatibilidade, mas a resolução oficial do tenant usa `companies`.
