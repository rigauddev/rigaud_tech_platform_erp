# Flutter Starter

Base inicial do frontend Flutter da Rigaud Tech Platform ERP.

## Plataformas

- Android
- iOS
- Web
- Windows
- Linux
- macOS

## Arquitetura

- Feature First
- MVVM
- Clean Architecture simplificada
- Riverpod para injeção de dependências e estado.
- GoRouter para navegação.
- Dio para cliente HTTP.
- Freezed para estados e modelos imutáveis.
- json_serializable para serialização futura.
- Responsive Framework para breakpoints responsivos.

## Estrutura

- `lib/app`: bootstrap, app root, configuração, router e tema.
- `lib/core`: API, erros, extensões, logs, rede, storage e utilitários.
- `lib/features`: features independentes organizadas por `data`, `domain` e `presentation`.
- `lib/shared`: componentes, layouts, modelos, providers e widgets compartilhados.

## Telas

- Splash inicial.
- Login visual responsivo.
- Dashboard placeholder.
- Página 404.

## Temas

- Tema claro.
- Tema escuro.

## Configuração por ambiente

Variáveis preparadas via `--dart-define`:

- `APP_NAME`
- `APP_ENV`
- `API_BASE_URL`
- `LOG_LEVEL`

Exemplo disponível em `erp-platform/frontend/.env.example`.

## HTTP

O Dio está preparado com:

- base URL por ambiente.
- timeout.
- request ID.
- interceptor de logs somente em desenvolvimento.
- interceptor preparado para token e refresh token futuro.
- padronização inicial de erros.

## Storage

Foram criadas abstrações para:

- armazenamento seguro de token.
- preferências do usuário.
- tema.
- idioma.
- tenant selecionado.

Modo offline não foi implementado. Uma etapa futura deverá usar armazenamento local e fila de sincronização.

## Testes

Comandos atuais:

```bash
flutter pub get
flutter analyze
flutter test
flutter build web
```

Comandos por plataforma para testes de integração futuros estão documentados em `docs/frontend/platforms.md`.

## Observações

Esta task cria somente o starter visual e arquitetural do frontend.

Nenhuma regra de negócio do ERP foi implementada.
