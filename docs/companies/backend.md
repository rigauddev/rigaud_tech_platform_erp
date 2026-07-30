# Companies Backend

## Camadas

- `domain`: status, exceptions e contratos de repository.
- `application`: normalização, validação e use cases.
- `infrastructure`: modelo SQLAlchemy, repository e bootstrap explícito.
- `presentation`: schemas e router FastAPI.

## Endpoints

- `POST /api/v1/companies`
- `GET /api/v1/companies`
- `GET /api/v1/companies/current`
- `GET /api/v1/companies/{company_id}`
- `PATCH /api/v1/companies/{company_id}`
- `POST /api/v1/companies/{company_id}/activate`
- `POST /api/v1/companies/{company_id}/deactivate`
- `POST /api/v1/companies/{company_id}/suspend`

Operações administrativas exigem `is_superuser = true`.

Usuário comum pode consultar somente a empresa do próprio tenant.
