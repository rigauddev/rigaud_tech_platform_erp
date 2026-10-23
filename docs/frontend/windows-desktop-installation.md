# Testando o Cliente Desktop no Windows

Este guia prepara um ambiente de desenvolvimento Windows para compilar e testar
o cliente Flutter da Rigaud Tech Platform ERP com a API local existente.

## Estado do instalador

O repositório ainda nao distribui um instalador Windows (`.msi`, `.msix` ou
`Setup.exe`). Portanto, nao ha um arquivo de instalacao para baixar ou executar.
O build Flutter gera uma pasta de aplicacao para testes; essa pasta nao e um
instalador registrado no Windows e nao deve ser distribuida como versao de
producao.

Windows e uma plataforma cliente do ERP. Para On-Premise, o servidor recomendado
continua sendo Linux; nao instale um PostgreSQL independente em cada computador
Windows.

## Pre-requisitos

- Windows 10 ou 11 de 64 bits.
- Git para Windows.
- Flutter 3.41.9 stable, com Dart 3.11.5, conforme o SDK usado pelo projeto.
- Visual Studio 2022 Community ou Build Tools com o workload **Desktop
  development with C++**, incluindo MSVC x64/x86, CMake e Windows SDK.
- Docker Desktop se a API local ainda nao estiver em execucao.
- Permissao para executar o Dart e as ferramentas do Flutter. Em computadores
  gerenciados, mantenha as politicas de seguranca e solicite autorizacao ao
  administrador de TI se o Windows bloquear essas ferramentas.

## Preparar as ferramentas

1. Instale o Git for Windows a partir da pagina oficial:
   <https://git-scm.com/download/win>.
2. Instale o Flutter stable seguindo o guia oficial:
   <https://docs.flutter.dev/platform-integration/windows/setup>.
   Use a versao 3.41.9 para corresponder ao SDK deste projeto. Extraia o SDK em
   uma pasta sem espacos, por exemplo `C:\src\flutter`, e adicione
   `C:\src\flutter\bin` ao `PATH` do usuario.
3. Abra o instalador do Visual Studio 2022 Community ou Build Tools e selecione
   **Desktop development with C++**. Confirme que os componentes incluem o
   compilador MSVC para x64/x86, o Windows 10/11 SDK e as ferramentas CMake.
   Referencia oficial:
   <https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools>.
4. Abra um novo PowerShell e verifique o ambiente:

   ```powershell
   flutter --version
   flutter doctor -v
   flutter config --enable-windows-desktop
   flutter devices
   ```

   `flutter devices` deve listar `Windows (desktop)`. Corrija os itens de
   Flutter Windows reportados por `flutter doctor` antes de continuar.
5. Se `dart.exe` for bloqueado por App Control/Device Guard, nao desative nem
   contorne essa protecao. Pare aqui e solicite a liberacao aprovada do SDK ao
   administrador responsavel. Sem executar Dart, nao e possivel compilar ou
   abrir o cliente nativo.

## Iniciar a API local

Use o workspace existente no Windows e o mesmo projeto Compose configurado no
repositorio; nao crie uma segunda stack.

1. Abra PowerShell na raiz do repositorio e verifique os servicos:

   ```powershell
   docker compose ps
   ```

2. Se backend, PostgreSQL e Redis ainda nao estiverem ativos, inicie os servicos
   pelo Compose da raiz do repositorio:

   ```powershell
   docker compose up -d backend postgres redis
   ```

3. Confirme que os servicos estao saudaveis e que a API responde:

   ```powershell
   Invoke-RestMethod http://localhost:8000/api/v1/health
   ```

   Se os servicos ja estiverem saudaveis, nao os reinicie.

## Executar o aplicativo no Windows

Execute estes comandos no PowerShell. O diretorio de trabalho precisa estar no
sistema de arquivos do Windows; nao execute o Flutter para Windows pelo shell
Linux do WSL.

```powershell
Set-Location .\erp-platform\frontend
flutter pub get
flutter run -d windows `
  --dart-define=APP_ENV=development `
  --dart-define=API_BASE_URL=http://localhost:8000
```

`API_BASE_URL` recebe a origem da API, sem o sufixo `/api/v1`. Para acessar um
servidor em outra maquina, use o endereco de rede autorizado do servidor e
confirme firewall, conectividade e TLS; `localhost` funciona somente quando a
API esta acessivel nesta mesma maquina.

## Gerar e abrir um build local de teste

Para criar a versao Release:

```powershell
flutter build windows --release `
  --dart-define=APP_ENV=development `
  --dart-define=API_BASE_URL=http://localhost:8000
```

O executavel do projeto deve ser gerado em:

```text
erp-platform\frontend\build\windows\x64\runner\Release\rigaud_tech_erp.exe
```

Execute-o mantendo no mesmo diretorio todos os arquivos gerados, incluindo as
DLLs e a pasta `data`. Copiar somente o `.exe` nao e suficiente. Este build
continua sendo local e de desenvolvimento; nao e um instalador nem uma versao
aprovada para distribuicao a clientes.

## Verificacao funcional

1. Confirme que a janela do aplicativo abre sem erros.
2. Entre com uma conta demo documentada em
   [Contas Demo](../demo/accounts.md); a senha compartilhada das contas demo
   tambem esta descrita nessa pagina.
3. Confirme que o login e as chamadas seguintes alcancam a API em
   `http://localhost:8000`.
4. Verifique a navegacao e o fechamento/reabertura do aplicativo.
5. Registre erros de Flutter, API ou plugins com a plataforma e o passo que os
   reproduz; nao inclua tokens, senhas ou outros dados sensiveis nos logs.

## Remocao

Como nao ha instalador, o build local nao cria entrada em **Aplicativos
instalados** nem atalho de producao. Feche o aplicativo e remova a pasta de
build de teste quando nao for mais necessaria. Nao apague o workspace, os dados
do PostgreSQL ou os volumes Docker para remover o cliente.

## O que falta para uma instalacao de usuario final

Uma task futura de distribuicao Windows deve definir e validar empacotamento
(por exemplo, MSIX ou MSI), assinatura de codigo, requisitos de runtime,
atualizacao, desinstalacao, atalho, configuracao segura do endereco da API e
publicacao do artefato. Esses itens nao sao criados por `flutter build windows`
e nao fazem parte deste guia de teste.

## Referencias

- [Flutter: configurar desenvolvimento Windows](https://docs.flutter.dev/platform-integration/windows/setup)
- [Flutter: suporte desktop](https://docs.flutter.dev/platform-integration/desktop)
- [Microsoft: componentes do workload C++ para Build Tools](https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools)
- [Flutter: plataformas do projeto](./platforms.md)
