# Application Navigation

UI-002 organiza a navegação compartilhada do ERP sem introduzir fluxos comerciais.

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

## Subtelas

Cadastros, detalhes e edições apresentam uma ação de voltar para sua lista ou tela-pai. A rota-pai é explícita para evitar depender de histórico do navegador, pois os fluxos do app utilizam GoRouter com navegação declarativa.

## Marca

`assets/images/logo_rigaud_tech_trimmed.png` é uma variante PNG com transparência preservada e sem a margem excedente do arquivo original. A tela de Login usa essa variante para exibir a marca sem escala ou recorte artificial.

## Limites

UI-002 não implementa PDV, atendimento de garçom, KDS, aplicativo do cliente, NF-e/XML, mesas, pedidos ou outras funcionalidades comerciais. Essas experiências pertencem às tasks próprias de Restaurant, POS e Fiscal.
