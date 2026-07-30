# Companies

Módulo de Empresas da Rigaud Tech Platform ERP.

Na DEV-006, `Company` passou a ser a raiz oficial do tenant.

## Camadas

- `domain`: status, exceptions e contratos.
- `application`: validações e use cases.
- `infrastructure`: modelo SQLAlchemy, repository e bootstrap explícito.
- `presentation`: schemas e router FastAPI.
- `tests`: reservado para testes internos do módulo.

## Regras Principais

- Company não possui `tenant_id`.
- `company.id` é usado como `tenant_id` nas entidades futuras.
- CNPJ é normalizado para dígitos.
- Slug e código resolvem tenant.
- Empresa inativa ou suspensa bloqueia novos logins.

## DEV-008

Companies usa respostas padronizadas e registra eventos de auditoria em criação, alteração e mudança de status.

## DEV-010

Companies também concentra a fundação de filiais e memberships:

- `BranchModel`
- `CompanyMembershipModel`
- `BranchMembershipModel`

`Company` continua sendo a raiz do tenant. Filiais não criam um novo tenant.
