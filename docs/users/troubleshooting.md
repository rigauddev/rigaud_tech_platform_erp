# Users Troubleshooting

## Login Bloqueado

Verifique:

- status da empresa;
- `auth_users.status`;
- `auth_users.is_active`;
- `auth_users.deleted_at`;
- `auth_users.locked_until`.

## Email Duplicado

Email é único por empresa.
Para o mesmo tenant, a API retorna conflito.

## Sessão Expirada Após Alteração

Bloqueio, desativação, troca de senha e reset de senha revogam refresh tokens ativos.
O usuário deve autenticar novamente.

## CodeSign macOS/iOS

Se o build nativo falhar com:

```text
resource fork, Finder information, or similar detritus not allowed
```

limpe atributos estendidos dentro do projeto:

```bash
xattr -cr erp-platform/frontend/macos erp-platform/frontend/ios erp-platform/frontend/build
```

Se o erro persistir, mova o workspace para uma pasta local fora de File Provider/iCloud e regenere dependências com `flutter pub get`.
