# Flutter Platforms

O projeto Flutter está habilitado para:

- Web
- Android
- iOS
- Windows
- Linux
- macOS

## Comandos

Web:

```bash
flutter run -d chrome
```

Android:

```bash
flutter run -d android
```

iOS:

```bash
flutter run -d ios
```

Windows:

```bash
flutter run -d windows
```

Linux:

```bash
flutter run -d linux
```

macOS:

```bash
flutter run -d macos
```

## Testes

Testes unitários e de widget atuais:

```bash
flutter test
```

Análise estática:

```bash
flutter analyze
```

Validação de build Web:

```bash
flutter build web
```

Testes de integração por plataforma, quando a pasta `integration_test/` existir:

Web:

```bash
flutter test integration_test -d chrome
```

Android:

```bash
flutter test integration_test -d android
```

iOS:

```bash
flutter test integration_test -d ios
```

Windows:

```bash
flutter test integration_test -d windows
```

Linux:

```bash
flutter test integration_test -d linux
```

macOS:

```bash
flutter test integration_test -d macos
```

## Pré-requisitos

- Android exige Android SDK e dispositivo/emulador.
- iOS exige macOS, Xcode e simulador/dispositivo.
- Windows exige ambiente Windows com toolchain desktop do Flutter.
- Linux exige toolchain GTK/CMake configurada.
- macOS exige macOS e Xcode.

Plugins multiplataforma podem ter suporte desigual entre sistemas operacionais. Antes de usar um plugin em regra de negócio, valide suporte por plataforma.
