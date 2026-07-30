# ADR 0003: Company como Raiz do Tenant

## Status

Aceita.

## Contexto

A autenticação da DEV-005 usava uma representação mínima de tenant em `auth_users.tenant_slug`.

A DEV-006 introduz o módulo Empresas. A empresa representa a organização principal da plataforma e precisa ser a fonte oficial para resolução do tenant.

## Decisão

`Company` é a raiz do tenant.

`Company` não possui `tenant_id`.

`company.id` é utilizado como `tenant_id` nas entidades tenant-aware.

Tenant é resolvido por `Company.slug` ou `Company.code`.

Empresas inativas ou suspensas bloqueiam novos logins.

Datas internas permanecem em UTC. `Company.timezone` será usada para apresentação e regras locais futuras.

## Consequências

- O frontend nunca envia UUID arbitrário como tenant confiável.
- A autenticação passa a resolver tenant pela tabela `companies`.
- O campo temporário `auth_users.tenant_slug` fica preservado por compatibilidade, mas deixa de ser a fonte oficial.
- Futuras entidades como usuários, produtos e vendas usarão `tenant_id = companies.id`.
