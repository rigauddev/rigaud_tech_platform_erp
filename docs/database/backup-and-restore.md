# Backup and Restore

Esta task não implementa backup nem restore.

## Política futura

- Backup diário.
- Backup antes de atualização.
- Backup manual.
- Cópia local.
- Cópia externa futura.
- Teste periódico de restauração.

## Comandos futuros

```bash
backup
restore
verify
```

## Docker

O volume persistente do PostgreSQL preserva dados entre reinícios, mas não substitui backup.

Não há upload para S3, credenciais AWS ou agendamentos automáticos nesta task.
