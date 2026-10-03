# Login Screen

UI-001 refina a tela de login sem alterar regra de negócio.

## Layout

- A tela ocupa 100% do viewport.
- O fundo é fixo e não rola.
- Em desktop, o card informativo e o card de login ficam centralizados lado a lado, com a mesma largura, altura, raio e sombra.
- Em telas compactas, o login permanece como foco principal para preservar a experiência sem scroll.
- O layout usa `FittedBox` para evitar overflow em telas menores.
- Ao abrir o teclado, apenas a área do formulário é reposicionada por `viewInsets`.
- Não há `SingleChildScrollView` na tela de login.

## Informativos

O carrossel lateral possui um primeiro card fixo de informativo do sistema e deixa os próximos cards preparados para informativos da empresa.

Os cards seguem o mesmo design visual do login e podem evoluir futuramente para conteúdo administrável com texto ou imagem, sem alterar o fluxo de autenticação.

## Idioma

A tela inicial possui seletor visual por bandeira com `BR PT` e `US EN`. A seleção é salva no dispositivo e atualiza integralmente os textos do Login, do carrossel informativo, da recuperação de senha e do menu de navegação compartilhado.

As próximas telas serão traduzidas no momento em que forem evoluídas; não devem misturar textos novos em inglês com textos existentes em português na mesma experiência.

## Recuperação de Senha

`/login/forgot-password` oferece a tela de solicitação de recuperação e o retorno para Login. O envio de email ainda depende de uma task de autenticação própria; enquanto isso, a tela informa explicitamente que o serviço não está disponível, sem simular uma recuperação concluída.

## Identidade Visual

O background usa gradiente claro, grade técnica, conexões e cartões discretos relacionados a ERP:

- vendas;
- estoque;
- restaurante;
- dispositivos;
- cloud;
- conectividade entre módulos.

A logo usada no Login é `assets/images/Rigaud_Tech_profile_transparent.png`, declarada no `pubspec.yaml` e exibida sem recorte ou escala artificial. O card de acesso e o carrossel usam altura compacta, sem espaçadores flexíveis que criem área vertical vazia.

Os campos adotam a cor primária do tema no preenchimento leve, no rótulo flutuante e nos ícones de prefixo.

## Rodapé

O rodapé exibe:

- versão;
- build;
- API;
- ambiente.

Os valores podem ser informados com `--dart-define`:

```bash
flutter run -d chrome \
  --dart-define=APP_VERSION=0.1.0 \
  --dart-define=BUILD_NUMBER=local \
  --dart-define=APP_ENV=development \
  --dart-define=API_BASE_URL=http://localhost:8000
```

## Validações

Executado na UI-001:

- `flutter analyze`;
- `flutter test`;
- `flutter build web`;
- `flutter build apk --debug`;
- `flutter build macos`.
- `flutter devices`, com Chrome, macOS e iPhone Simulator detectados.

No macOS, quando o build falhar com `resource fork, Finder information, or similar detritus not allowed`, limpar xattrs do bundle gerado:

```bash
xattr -dr com.apple.FinderInfo build/macos/Build/Products/Release/rigaud_tech_erp.app
xattr -dr 'com.apple.fileprovider.fpfs#P' build/macos/Build/Products/Release/rigaud_tech_erp.app
flutter build macos
```

O iOS Simulator foi detectado, mas `flutter build ios --simulator` ainda falha neste workspace sincronizado quando o Flutter assina `Flutter.framework` e `build/native_assets/ios/objective_c.framework`. O `ios/Podfile` inclui limpeza de xattrs para Pods, mas a falha restante ocorre em artefatos gerados pelo próprio Flutter antes dos build phases do Xcode.

Windows e Linux não foram buildados nesta máquina por incompatibilidade de sistema operacional.
