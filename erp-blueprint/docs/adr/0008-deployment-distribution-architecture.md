# ADR 0008: Deployment And Distribution Architecture

## Status

Aceita.

## Contexto

A Rigaud Tech Platform ERP precisa suportar SaaS, deployments dedicados, On-Premise e Hybrid sem quebrar multi-tenancy, autenticação, auditoria, dados historicos ou o roadmap comercial.

Tambem existe necessidade real de preparar Production MVP, Financial MVP, HR MVP e AI/MCP sem acoplar deployment a tenant.

## Decisao

Separar oficialmente:

```text
Tenant = Company
Deployment = ambiente tecnico
```

Tipos de deployment:

- `CLOUD_SHARED`;
- `CLOUD_DEDICATED`;
- `ON_PREMISE`;
- `HYBRID`.

O tenant permanece `Company`, com `tenant_id = companies.id`.

Partner/Reseller nao e tenant.

O servidor recomendado para On-Premise em producao e Linux.

Production Engine sera independente de Restaurant. Restaurant consumira Production e Inventory.

## Consequencias

- Usuario comum nao escolhe empresa no login.
- O backend resolve tenant, filial, role, permissoes e escopo.
- Um tenant pode migrar entre deployments sem criar nova empresa.
- SaaS pode crescer por deployment stamps.
- On-Premise e Hybrid ficam preparados sem criar fork de produto.
- Offline-First completo continua futuro.
- AI/MCP deve respeitar tenant, branch, role, permissions e audit.
