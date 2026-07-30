# Multi-tenancy

Estratégia oficial do MVP:

```text
PostgreSQL compartilhado
+ schema compartilhado
+ tenant_id nas entidades pertencentes à empresa
```

## Tenant context

`app/database/tenant.py` usa `contextvars`, seguro para execução assíncrona.

Operações disponíveis:

- definir tenant atual.
- obter tenant atual.
- limpar tenant ao final da requisição.
- exigir tenant e falhar de forma controlada quando ausente.

## Company como raiz

Na DEV-006, `Company` passou a ser a raiz do tenant.

`Company` não possui `tenant_id`.

Entidades tenant-aware futuras usarão:

```text
tenant_id = companies.id
```

## Limites atuais

Ainda não há filtros tenant automáticos em todos os repositories.

O módulo de permissões completo ainda será implementado em Task futura.
