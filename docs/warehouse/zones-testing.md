# Warehouse Zones Testing

Validações da REST-005:

Backend:

- criação de zona;
- normalização de código;
- conflito por código no mesmo depósito;
- bloqueio de depósito de outra filial;
- reordenação.

Frontend:

- controller lista zonas;
- controller cria zona;
- controller reordena zona;
- navegação exibe item de menu `Zonas`.

Comandos:

```bash
make format
make lint
make test
flutter analyze
flutter test
flutter build web
flutter build apk --debug
flutter build macos
make check-task TASK=REST-005
```

Windows e Linux devem ser validados em ambientes próprios.
