# Users Rules

- O usuário pertence a uma empresa.
- `tenant_id` é sempre o `id` da empresa.
- Email é único por empresa.
- Email é armazenado em lowercase.
- O mesmo email pode existir em empresas diferentes.
- `status=active` permite autenticação.
- `status=inactive` e `status=blocked` impedem autenticação.
- `is_active` acompanha o status para compatibilidade.
- Bloqueio e desativação revogam sessões ativas.
- Troca e reset de senha revogam sessões ativas.
- Não há RBAC completo nesta etapa; apenas `is_superuser`.
