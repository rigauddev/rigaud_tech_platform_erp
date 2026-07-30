# Release Flow

Após merge aprovado em `main`:

```bash
git checkout main
git pull --ff-only origin main
```

Quando aplicável, criar tag:

```bash
git tag -a v<versao> -m "Rigaud Tech Platform ERP v<versao>"
git push origin v<versao>
```

Não inventar versão sem seguir o versionamento oficial.

## Validação Integrada em develop

Após merge da task em `develop`, executar:

```bash
docker compose config
alembic upgrade head
pytest
ruff check .
ruff format --check .
flutter analyze
flutter test
flutter build web
make check-task TASK=<TASK-ID>
```

Executar testes nativos disponíveis para as plataformas oficiais.
