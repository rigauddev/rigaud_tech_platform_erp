# Academy: Empresa como Tenant

## Conceito

Em uma plataforma multi-tenant, vários clientes usam a mesma aplicação e o mesmo banco, mas seus dados precisam permanecer logicamente isolados.

Na Rigaud Tech Platform ERP, a empresa é o tenant.

```text
Company.id
    ↓
tenant_id das entidades futuras
```

## Slug, Código e UUID

O usuário informa slug ou código no login.

O backend resolve a empresa:

```text
slug ou código
    ↓
companies
    ↓
company.id
```

O frontend não deve enviar um UUID arbitrário para escolher tenant.

## CNPJ

O CNPJ é normalizado e armazenado somente com dígitos.

Constraints no banco impedem duplicidade de:

- CNPJ.
- slug.
- código.

## Status

Status disponíveis:

- `active`
- `inactive`
- `suspended`

Somente empresa ativa permite novos logins.

## UTC e Timezone

Datas internas ficam em UTC.

`Company.timezone` indica como datas serão apresentadas ou interpretadas em regras locais futuras.

## SaaS e On-Premises

No SaaS, Flutter Web, Desktop e Mobile acessam a mesma API.

No on-premises, a empresa pode ter um servidor local único com FastAPI e PostgreSQL.

Não existe PostgreSQL por computador.

## Segurança

Administrar empresas exige superuser até o módulo de permissões completo.

Usuário comum consulta somente a própria empresa.
