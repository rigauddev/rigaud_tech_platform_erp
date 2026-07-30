# Companies Database

Tabela: `companies`.

`Company` é global e não possui `tenant_id`.

Constraints:

- `uq_companies_document`
- `uq_companies_slug`
- `uq_companies_code`
- `ck_companies_document_len`
- `ck_companies_status`

Migration:

- `0004_companies`
