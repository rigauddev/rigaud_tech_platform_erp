# Cloud Deployment

Cloud e o modelo SaaS central da Rigaud Tech Platform ERP.

## Arquitetura

```text
Flutter Web/Mobile/Desktop
        ↓
Rigaud Cloud
        ↓
FastAPI
        ↓
PostgreSQL
Redis
Workers
AI/MCP futuro
```

## Modelo Oficial

O Cloud inicial sera `CLOUD_SHARED`, com varios tenants no mesmo deployment e isolamento logico por `tenant_id`.

`CLOUD_DEDICATED` fica reservado para clientes que exijam isolamento operacional maior, requisitos regulatórios, volume dedicado ou contrato especial.

## Isolamento Obrigatorio

- Todas as entidades tenant-aware usam `tenant_id`.
- Backend resolve tenant pelo usuario autenticado.
- Frontend nunca envia `tenant_id` confiavel.
- Logs, auditoria, eventos e futuras filas devem carregar tenant e filial quando aplicavel.

## Deployment Stamps

O crescimento SaaS deve considerar deployment stamps:

```text
Control Plane
    ↓
Tenant Mapping
    ↓
Stamp A
Stamp B
Stamp C
```

Cada stamp pode conter um conjunto de tenants e sua propria infraestrutura. Isso prepara escala, isolamento progressivo, rollout controlado e reducao de impacto entre grupos de clientes.

## Fora Do Escopo DOC-008

- provisionamento real de cloud;
- Kubernetes;
- Terraform/Bicep;
- billing real;
- Kafka real;
- MCP real.
