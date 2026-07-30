# Authentication Troubleshooting

## Login retorna 401

Verifique:

- `tenant` correto.
- email normalizado.
- usuário ativo.
- senha correta.
- migration `0003_auth_tenant_slug_email` aplicada.

## Refresh retorna 401

Possíveis causas:

- refresh token expirado.
- refresh token já rotacionado.
- refresh token revogado por logout.
- token ausente do storage seguro no frontend.

## Flutter no Container

Se o Flutter reclamar de `safe.directory`, execute:

```bash
docker compose --env-file .env.example exec -T frontend git config --global --add safe.directory /sdks/flutter
```
