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
- `POST /api/v1/companies/branches`
- `GET /api/v1/companies/branches`

Operações administrativas exigem `is_superuser = true`.

Usuário comum pode consultar somente a empresa do próprio tenant.

## Filiais

`Branch` representa loja, filial, unidade ou matriz operacional dentro de uma empresa.

Regras técnicas atuais:

- `tenant_id` aponta para `companies.id`.
- `code` é único por tenant.
- apenas uma filial do tipo `headquarters` pode existir por tenant.
- `document` é único por tenant quando informado.
- filiais inativas não podem ser selecionadas como contexto ativo.

Não há estoque, venda, fiscal ou regra operacional por filial nesta task.
