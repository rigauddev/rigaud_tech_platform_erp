# Companies API

Endpoints:

- `POST /api/v1/companies`
- `GET /api/v1/companies`
- `GET /api/v1/companies/current`
- `GET /api/v1/companies/{company_id}`
- `PATCH /api/v1/companies/{company_id}`
- `POST /api/v1/companies/{company_id}/activate`
- `POST /api/v1/companies/{company_id}/deactivate`
- `POST /api/v1/companies/{company_id}/suspend`

Payload de criação:

```json
{
  "legal_name": "Rigaud Tecnologia Ltda",
  "trade_name": "Rigaud Tech",
  "document": "11222333000181",
  "email": "contato@empresa.com.br",
  "phone": "75982165869",
  "slug": "rigaud-tech",
  "code": "RIGAUD",
  "timezone": "America/Sao_Paulo",
  "locale": "pt-BR",
  "currency": "BRL"
}
```
