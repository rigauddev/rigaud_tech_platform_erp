# Audit

Módulo transversal de auditoria da Rigaud Tech Platform ERP.

Registra eventos relevantes em `audit_events` e expõe consulta administrativa somente para superusuários.

## Camadas

- `domain`: contratos.
- `application`: `AuditService`.
- `infrastructure`: modelo e repository SQLAlchemy.
- `presentation`: endpoints FastAPI.
