# Preparando e testando o cliente Windows

## Objetivo

Preparar um ambiente Windows para executar localmente o cliente desktop Flutter
da Rigaud Tech Platform ERP, sem confundir build de desenvolvimento com um
instalador distribuivel ou com um servidor On-Premise.

## Ferramentas

O desenvolvedor precisa de Windows 10/11 x64, Flutter 3.41.9 stable, Dart
3.11.5 e Visual Studio 2022 Community ou Build Tools com **Desktop development
with C++**, MSVC x64/x86, CMake e Windows SDK. A API local usa a stack Compose
ja existente.

Se uma politica corporativa bloquear a execucao de Dart, nao a desative. Solicite
ao administrador uma autorizacao compativel com a politica da organizacao.

## Fluxo de desenvolvimento

1. Confirme Flutter, compilador e dispositivo:

   ```powershell
   flutter doctor -v
   flutter config --enable-windows-desktop
   flutter devices
   ```

2. Confirme que a API local esta saudavel na porta `8000`, sem iniciar uma
   segunda stack Compose.
3. No diretorio `erp-platform\frontend`, resolva as dependencias e rode o
   cliente:

   ```powershell
   flutter pub get
   flutter run -d windows `
     --dart-define=APP_ENV=development `
     --dart-define=API_BASE_URL=http://localhost:8000
   ```

4. Teste login, chamadas da API, navegacao e encerramento do aplicativo.
   Utilize as contas demo documentadas em `docs/demo/accounts.md` e nao
   compartilhe credenciais ou tokens em logs.
5. Para produzir uma pasta Release local:

   ```powershell
   flutter build windows --release `
     --dart-define=APP_ENV=development `
     --dart-define=API_BASE_URL=http://localhost:8000
   ```

   O executavel tem como destino esperado
   `erp-platform\frontend\build\windows\x64\runner\Release\rigaud_tech_erp.exe`.
   Preserve junto dele as DLLs e a pasta `data`.

## Limite de distribuicao

O build acima nao produz MSI, MSIX ou assistente de instalacao. A pasta Release
serve para desenvolvimento e QA, nao para instalacao em clientes. Distribuicao
final depende de uma task propria para empacotamento, assinatura, atualizacao,
desinstalacao, runtime e configuracao do endpoint.

## Referencias

- Guia operacional complementar: `docs/frontend/windows-desktop-installation.md`.
- [Documentacao oficial Flutter para Windows](https://docs.flutter.dev/platform-integration/windows/setup)
- [Documentacao oficial Flutter para desktop](https://docs.flutter.dev/platform-integration/desktop)
