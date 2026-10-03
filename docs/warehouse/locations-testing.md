# Warehouse Locations Testing

Validações da REST-006:

```bash
make format
make lint
make test
flutter analyze
flutter test
flutter build web
flutter build apk --debug
flutter build macos
make check-task TASK=REST-006
```

Limitações:

- builds Windows e Linux devem ser validados em hosts compatíveis;
- leitura real por câmera de QR Code ou código de barras não faz parte da REST-006.

Coberturas esperadas:

- criação com normalização de código;
- duplicidade de código por depósito;
- isolamento por filial;
- validação de zona no depósito;
- ativação;
- inativação;
- soft delete;
- controller Flutter.
