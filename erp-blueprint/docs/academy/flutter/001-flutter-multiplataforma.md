# Flutter Multiplataforma

Flutter permite compartilhar a maior parte da base de código entre Web, Android, iOS, Windows, Linux e macOS.

## O que é compartilhado

- Widgets.
- Temas.
- Navegação.
- Estado.
- Regras de apresentação.
- Cliente HTTP.
- Modelos e contratos.

## O que muda por plataforma

- Empacotamento.
- Permissões.
- Toolchain de build.
- Integrações nativas.
- Disponibilidade de plugins.
- Comportamento de input, teclado, janelas e ciclo de vida.

## Executar no Web

```bash
flutter run -d chrome
```

## Executar no Windows

```bash
flutter run -d windows
```

Requer ambiente Windows com suporte desktop habilitado no Flutter.

## Executar no Linux

```bash
flutter run -d linux
```

Requer bibliotecas GTK, CMake e toolchain C++.

## Executar no macOS

```bash
flutter run -d macos
```

Requer macOS e Xcode.

## Limitações de plugins

Nem todo plugin Flutter suporta todas as plataformas. Antes de usar recursos como storage seguro, conectividade, câmera, impressão ou recursos do sistema operacional, confirme a matriz de compatibilidade do plugin.

Esta aula é introdutória e não implementa funcionalidades do ERP.
