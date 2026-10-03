# Cloud

Documento de entrada para deployment Cloud.

Detalhes tecnicos estao em `docs/architecture/deployment/cloud.md`.

## Principio

Cloud e o modelo SaaS multi-tenant da Rigaud Tech Platform ERP.

## Variantes

- `CLOUD_SHARED`;
- `CLOUD_DEDICATED`.

## Regra

Todo acesso cloud deve preservar isolamento por tenant, filial ativa, role, permissions, auditoria e logs estruturados.
