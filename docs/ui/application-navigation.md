# Application Navigation

UI-002 organiza a navegação compartilhada do ERP sem introduzir fluxos comerciais.

Antes de alterações, a equipe confirma branch, upstream remoto, roadmap e backlog. Quando uma mudança requer recarga, apenas o container afetado é reiniciado; a stack Docker existente não deve ser duplicada.

## Entrada

A Splash apenas apresenta a marca enquanto a aplicação inicializa. Ela redireciona automaticamente para Login ou Dashboard conforme a guarda de rota; não existe uma ação manual de continuar.

## Menu

O menu lateral agrupa as áreas pelo contexto de trabalho:

- Visão geral: Dashboard.
- Cadastros: Empresas, Usuários, Produtos e Categorias.
- Estoque: saldos, transações, recebimentos, depósitos, zonas e localizações.
- Conta e segurança: perfil e autenticação em dois fatores.
- Administração: auditoria.
- Desenvolvimento: Ambiente demo, apenas fora de produção.

`Ambiente demo` instala, consulta e remove dados fictícios. Não é um módulo comercial e não deve ser disponibilizado a clientes em produção.

O menu usa o contexto autenticado para não exibir Empresa, Usuários, Auditoria e Ambiente demo a perfis sem acesso de plataforma. O papel técnico ativo é mostrado abaixo da marca. A autorização da API continua sendo a fonte de segurança; esta filtragem evita links que a própria guarda de rota já bloquearia.

A autenticação em dois fatores pertence a **Conta e segurança**, junto de Meu perfil. Ela não faz parte dos menus operacionais de estoque, restaurante ou varejo.

## Padrão operacional do Restaurante

As telas de Restaurante seguem o desenho aprovado para Setores e Ambientes: título e contexto da filial, indicadores pequenos para leitura rápida, cartões de operação e uma tabela em desktop que se transforma em cartões em telas menores. As entradas de menu permanecem agrupadas por contexto operacional, sem misturar conta, segurança ou ferramentas de desenvolvimento.

Esse padrão será aplicado a cada tela nova ou revisada no próprio escopo da task correspondente; ele não exige uma reescrita ampla de telas já entregues.

## Subtelas

Cadastros, detalhes e edições apresentam uma ação de voltar para sua lista ou tela-pai. A rota-pai é explícita para evitar depender de histórico do navegador, pois os fluxos do app utilizam GoRouter com navegação declarativa.

## Marca

`assets/images/rigaud-tech-logo.png` é a marca selecionada para a tela de Login e está declarada no `pubspec.yaml`. A imagem é exibida sem recorte ou escala artificial.

## Limites

UI-002 não implementa PDV, atendimento de garçom, KDS, aplicativo do cliente, NF-e/XML, mesas, pedidos ou outras funcionalidades comerciais. Essas experiências pertencem às tasks próprias de Restaurant, POS e Fiscal.
