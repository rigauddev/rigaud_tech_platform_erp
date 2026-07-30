# Companies Security

## Permissão Temporária

Até o módulo completo de permissões:

- Administração de empresas exige `is_superuser = true`.
- Usuário comum consulta apenas `/api/v1/companies/current`.
- Usuário comum pode consultar por ID somente a própria empresa.

## Dados

- CNPJ é armazenado somente com dígitos.
- CNPJ não deve ser registrado em logs de auditoria.
- Erros SQL são convertidos em responses controladas.
- Listagem possui limite de página.

## Status

Fonte oficial: `status`.

`is_active` foi mantido como compatibilidade operacional derivada:

- `active`: `is_active = true`
- `inactive`: `is_active = false`
- `suspended`: `is_active = false`
