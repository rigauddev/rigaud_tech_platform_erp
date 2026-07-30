# ERP Platform Frontend

Frontend Flutter da Rigaud Tech Platform ERP.

## Plataformas

- Android
- iOS
- Web
- Windows
- Linux
- macOS

## Stack

- Flutter
- Dart
- MVVM
- Riverpod para injeção de dependências e estado.
- GoRouter para navegação centralizada.
- Dio para HTTP.
- Freezed e json_serializable.
- flutter_secure_storage e shared_preferences.
- intl, logging e connectivity_plus.
- Responsive Framework

## Estrutura

- `lib/app`: aplicação, bootstrap, router, tema e configuração por ambiente.
- `lib/core`: API, rede, erros, logging, storage, constantes e utilitários.
- `lib/features`: features independentes da aplicação.
- `lib/shared`: componentes, layouts, modelos, providers e widgets compartilhados.

Cada feature segue `data`, `domain` e `presentation`.

## Telas iniciais

- Splash Screen
- Login Screen visual
- Dashboard placeholder
- Página 404

Até DEV-006, o frontend contém autenticação inicial e telas administrativas de empresas.

## Execução

Web:

```bash
flutter run -d chrome --dart-define=APP_ENV=development --dart-define=API_BASE_URL=http://localhost:8000
```

Docker Web:

```bash
make up
```

## Testes

```bash
flutter pub get
flutter analyze
flutter test
flutter build web
```

Os comandos de testes por plataforma para fluxos de integração futuros estão em `docs/frontend/platforms.md`.

## Docker

O Dockerfile de desenvolvimento do Flutter Web fica em `docker/flutter/Dockerfile`, na raiz do workspace.
