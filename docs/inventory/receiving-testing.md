# Receiving Testing

Validações da REST-007:

```bash
make format
make lint
make test
flutter analyze
flutter test
flutter build web
flutter build apk --debug
flutter build macos
make check-task TASK=REST-007
```

## Cobertura

Backend:

- normalização de número do documento;
- validação de duplicidade por tenant e filial;
- validação de depósito da filial ativa;
- validação de quantidade pendente;
- mudança de status;
- soft delete;
- garantia de não criar movimento nem alterar saldo.

Frontend:

- controller Riverpod;
- listagem;
- criação;
- mudança de status.

Builds desktop devem ser executados apenas em sistemas compatíveis com a plataforma de destino.
