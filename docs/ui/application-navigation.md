# Application Navigation

UI-002 organiza a navegação compartilhada do ERP sem introduzir fluxos comerciais.

Antes de alterações, a equipe confirma branch, upstream remoto, roadmap e backlog. Quando uma mudança requer recarga, apenas o container afetado é reiniciado; a stack Docker existente não deve ser duplicada.

## Entrada

A Splash apenas apresenta a marca enquanto a aplicação inicializa. Ela redireciona automaticamente para Login ou Dashboard conforme a guarda de rota; não existe uma ação manual de continuar.

## Menu

O menu lateral usa navegação direta e contextual, seguindo o layout visual
aprovado: Início, Vendas, Restaurante, Estoque, Financeiro, Relatórios e
Configurações. Ao acessar uma tela de Restaurante, esse contexto fica aberto e
mostra Visão geral, Mesas, Setores e ambientes, Garçons e equipe, Cardápio,
Pedidos e Delivery. A rota atual recebe faixa e texto azuis; a navegação de
Conta e MFA fica dentro de Configurações e Perfil, não no menu operacional.

`Ambiente demo` instala, consulta e remove dados fictícios. Não é um módulo comercial e não deve ser disponibilizado a clientes em produção.

As opções futuras de Cardápio, Pedidos e Delivery permanecem visíveis como
mapa do fluxo operacional, mas só terão interação quando as respectivas tasks
forem entregues. A autorização da API continua sendo a fonte de segurança;
visibilidade de menu não concede permissão.

A autenticação em dois fatores pertence a **Conta e segurança**, junto de Meu perfil. Ela não faz parte dos menus operacionais de estoque, restaurante ou varejo.

## Padrão operacional do Restaurante

As telas de Restaurante seguem o desenho aprovado para Setores e Ambientes: título e contexto da filial, indicadores pequenos para leitura rápida, cartões de operação e uma tabela em desktop que se transforma em cartões em telas menores. As entradas de menu permanecem agrupadas por contexto operacional, sem misturar conta, segurança ou ferramentas de desenvolvimento.

Esse padrão será aplicado a cada tela nova ou revisada no próprio escopo da task correspondente; ele não exige uma reescrita ampla de telas já entregues.

## Subtelas

Cadastros, detalhes e edições apresentam uma ação de voltar para sua lista ou tela-pai. A rota-pai é explícita para evitar depender de histórico do navegador, pois os fluxos do app utilizam GoRouter com navegação declarativa.

## Idioma e marca

O Login possui seletor por bandeira: `BR PT` e `US EN`. A escolha é persistida
localmente e atualiza Login, recuperação de senha, menu compartilhado e as
telas que já aderiram ao catálogo de textos. Toda tela alterada deve usar
`AppStrings`; não deve incluir textos novos fixos em apenas um idioma.

`assets/images/Rigaud_Tech_profile_transparent.png` é a variante sem fundo
usada no shell e no Login. Ela é gerada a partir da marca fornecida e declarada
no `pubspec.yaml`.

## Limites

UI-002 não implementa PDV, atendimento de garçom, KDS, aplicativo do cliente, NF-e/XML, mesas, pedidos ou outras funcionalidades comerciais. Essas experiências pertencem às tasks próprias de Restaurant, POS e Fiscal.
