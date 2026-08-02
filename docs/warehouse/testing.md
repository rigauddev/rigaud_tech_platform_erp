# Warehouse Testing

Validações da REST-004:

Backend:

- criação de depósito;
- normalização de código;
- conflito por código na mesma filial;
- definição de depósito padrão;
- seed demo idempotente com depósitos por filial.

Frontend:

- controller lista depósitos;
- controller cria depósito;
- navegação exibe item de menu `Depósitos`.

Comandos:

```bash
make lint
make format
make test
flutter analyze
flutter test
flutter build web
flutter build apk --debug
flutter build macos
make check-task TASK=REST-004
```

`make test` executa `alembic upgrade head` antes do reset demo e do Pytest para garantir que as tabelas de estoque e depósitos existam no banco local.

No macOS, se o build falhar em `CodeSign` com `resource fork, Finder information, or similar detritus not allowed`, limpe os atributos estendidos do frontend com:

```bash
xattr -cr erp-platform/frontend
```

Windows e Linux devem ser validados em ambientes próprios. A feature não adiciona dependências específicas de sistema operacional.
