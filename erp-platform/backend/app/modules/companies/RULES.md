# Companies Rules

- Company é a raiz do tenant.
- Company não possui `tenant_id`.
- `company.id` é utilizado como `tenant_id`.
- CNPJ é armazenado somente com dígitos.
- Slug é minúsculo e único.
- Código é maiúsculo e único.
- Empresa inativa bloqueia login.
- Empresa suspensa bloqueia login.
- Administração exige superuser.
- Usuário comum consulta somente a própria empresa.
