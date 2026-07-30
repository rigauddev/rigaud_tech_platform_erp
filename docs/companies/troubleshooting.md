# Companies Troubleshooting

## Erro 409

Documento, slug ou código já existe.

## Login retorna 403

Verifique se a empresa está:

- ativa;
- com `is_active = true`;
- não suspensa;
- resolvida pelo slug ou código informado.

## Usuário comum não lista empresas

Comportamento esperado. Listagem geral é administrativa e exige superuser.

Usuário comum deve usar `/api/v1/companies/current`.
