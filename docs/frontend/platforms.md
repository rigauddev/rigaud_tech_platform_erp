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
flutter emulators
flutter emulators --launch Pixel_9_Pro_XL
flutter run -d emulator-5554 --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

iOS:

```bash
flutter devices
flutter run -d ios --dart-define=API_BASE_URL=http://localhost:8000
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
flutter run -d macos --dart-define=API_BASE_URL=http://localhost:8000
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

## Docker e Execucao Local

Os comandos Flutter executados no container podem recriar `.dart_tool/package_config.json` com caminhos internos, como `/sdks/flutter` e `/root/.pub-cache`.

Antes de rodar Android, iOS ou macOS diretamente no host, execute:

```bash
flutter pub get
```

## CodeSign macOS/iOS

Se o workspace estiver em pasta sincronizada por File Provider/iCloud, o Xcode pode falhar no CodeSign com:

```text
resource fork, Finder information, or similar detritus not allowed
```

Use uma cópia do projeto fora da pasta sincronizada ou mova o workspace para um diretório local não sincronizado antes de rodar:

```bash
flutter run -d macos --dart-define=API_BASE_URL=http://localhost:8000
flutter run -d ios --dart-define=API_BASE_URL=http://localhost:8000
```

## Pré-requisitos

- Android exige Android SDK e dispositivo/emulador.
- iOS exige macOS, Xcode e simulador/dispositivo.
- Windows exige ambiente Windows com toolchain desktop do Flutter.
- Linux exige toolchain GTK/CMake configurada.
- macOS exige macOS e Xcode.

Plugins multiplataforma podem ter suporte desigual entre sistemas operacionais. Antes de usar um plugin em regra de negócio, valide suporte por plataforma.
