import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app_language.dart';

final appStringsProvider = Provider<AppStrings>((ref) {
  return AppStrings(ref.watch(appLanguageProvider));
});

class AppStrings {
  const AppStrings(this.language);

  final AppLanguage language;

  bool get isPortuguese => language == AppLanguage.portuguese;

  String get appName => 'Rigaud Tech Platform ERP';
  String get dashboard => isPortuguese ? 'Dashboard' : 'Dashboard';
  String get back => isPortuguese ? 'Voltar' : 'Back';
  String get overview => isPortuguese ? 'Visão geral' : 'Overview';
  String get records => isPortuguese ? 'Cadastros' : 'Records';
  String get inventory => isPortuguese ? 'Estoque' : 'Inventory';
  String get accountSecurity =>
      isPortuguese ? 'Conta e segurança' : 'Account & security';
  String get administration =>
      isPortuguese ? 'Administração' : 'Administration';
  String get development => isPortuguese ? 'Desenvolvimento' : 'Development';
  String get companies => isPortuguese ? 'Empresas' : 'Companies';
  String get users => isPortuguese ? 'Usuários' : 'Users';
  String get products => isPortuguese ? 'Produtos' : 'Products';
  String get categories => isPortuguese ? 'Categorias' : 'Categories';
  String get balancesTransactions =>
      isPortuguese ? 'Saldos e transações' : 'Balances & transactions';
  String get receiving => isPortuguese ? 'Recebimentos' : 'Receiving';
  String get warehouses => isPortuguese ? 'Depósitos' : 'Warehouses';
  String get zones => isPortuguese ? 'Zonas' : 'Zones';
  String get locations => isPortuguese ? 'Localizações' : 'Locations';
  String get myProfile => isPortuguese ? 'Meu perfil' : 'My profile';
  String get mfa => isPortuguese
      ? 'Autenticação em dois fatores'
      : 'Two-factor authentication';
  String get audit => isPortuguese ? 'Auditoria' : 'Audit';
  String get demoEnvironment =>
      isPortuguese ? 'Ambiente demo' : 'Demo environment';
  String get platformAdministrator =>
      isPortuguese ? 'Administrador da plataforma' : 'Platform administrator';
  String get companyAdministrator =>
      isPortuguese ? 'Administrador da empresa' : 'Company administrator';
  String get branchManager =>
      isPortuguese ? 'Gerente da filial' : 'Branch manager';
  String get branchOperator =>
      isPortuguese ? 'Operador da filial' : 'Branch operator';
  String get authenticatedUser =>
      isPortuguese ? 'Usuário autenticado' : 'Authenticated user';
  String get home => isPortuguese ? 'Início' : 'Home';
  String get sales => isPortuguese ? 'Vendas' : 'Sales';
  String get restaurant => isPortuguese ? 'Restaurante' : 'Restaurant';
  String get restaurantOverview => isPortuguese ? 'Visão geral' : 'Overview';
  String get tables => isPortuguese ? 'Mesas' : 'Tables';
  String get sectorsEnvironments =>
      isPortuguese ? 'Setores e ambientes' : 'Sectors & environments';
  String get staffTeam => isPortuguese ? 'Garçons e equipe' : 'Waiters & team';
  String get menu => isPortuguese ? 'Cardápio' : 'Menu';
  String get orders => isPortuguese ? 'Pedidos' : 'Orders';
  String get delivery => 'Delivery';
  String get finance => isPortuguese ? 'Financeiro' : 'Finance';
  String get reports => isPortuguese ? 'Relatórios' : 'Reports';
  String get settings => isPortuguese ? 'Configurações' : 'Settings';
  String get searchSystem =>
      isPortuguese ? 'Pesquisar no sistema...' : 'Search the system...';
  String get notifications => isPortuguese ? 'Notificações' : 'Notifications';
  String get help => isPortuguese ? 'Ajuda' : 'Help';
  String get staffBreadcrumb => isPortuguese
      ? 'Restaurante  >  Garçons e equipe'
      : 'Restaurant  >  Waiters & team';
  String get staffTitle => isPortuguese ? 'Garçons e equipe' : 'Waiters & team';
  String get staffDescription => isPortuguese
      ? 'Organize a equipe de atendimento e acompanhe a operação por setor.'
      : 'Organize the service team and track operations by sector.';
  String get newWaiter => isPortuguese ? 'Novo garçom' : 'New waiter';
  String get professionals => isPortuguese ? 'Profissionais' : 'Professionals';
  String get totalRegistered =>
      isPortuguese ? 'Total cadastrados' : 'Total registered';
  String get serving => isPortuguese ? 'Em atendimento' : 'Serving';
  String get teamLabel => isPortuguese ? 'da equipe' : 'of the team';
  String get sectorsCovered =>
      isPortuguese ? 'Setores cobertos' : 'Covered sectors';
  String get activeTeam =>
      isPortuguese ? 'Com equipe ativa' : 'With active team';
  String get paused => isPortuguese ? 'Em pausa' : 'Paused';
  String get operationalTeam =>
      isPortuguese ? 'Equipe operacional' : 'Operational team';
  String get searchProfessional =>
      isPortuguese ? 'Buscar profissional...' : 'Search professional...';
  String get professional => isPortuguese ? 'Profissional' : 'Professional';
  String get function => isPortuguese ? 'Função' : 'Role';
  String get currentSector => isPortuguese ? 'Setor atual' : 'Current sector';
  String get actions => isPortuguese ? 'Ações' : 'Actions';
  String get noSector => isPortuguese ? 'Sem setor' : 'No sector';
  String get available => isPortuguese ? 'Disponível' : 'Available';
  String get waiter => isPortuguese ? 'Garçom' : 'Waiter';
  String get attendant => isPortuguese ? 'Atendente' : 'Attendant';
  String get manager => isPortuguese ? 'Gerente' : 'Manager';
  String get name => isPortuguese ? 'Nome' : 'Name';
  String get code => isPortuguese ? 'Código' : 'Code';
  String get cancel => isPortuguese ? 'Cancelar' : 'Cancel';
  String get save => isPortuguese ? 'Salvar' : 'Save';
  String get unableToLoadStaff => isPortuguese
      ? 'Não foi possível carregar a equipe.'
      : 'Unable to load the team.';
  String get unableToSaveStaff => isPortuguese
      ? 'Não foi possível salvar o profissional.'
      : 'Unable to save the professional.';
  String get dailyMenu => isPortuguese ? 'Menu do dia' : 'Daily menu';
  String get menuAvailabilityDescription => isPortuguese
      ? 'Publique os itens disponíveis para venda e acompanhe as cotas comerciais da operação.'
      : 'Publish items available for sale and track commercial quotas.';
  String get addItem => isPortuguese ? 'Adicionar item' : 'Add item';
  String get publishedItems =>
      isPortuguese ? 'Itens publicados' : 'Published items';
  String get availableItems => isPortuguese ? 'Disponíveis' : 'Available';
  String get limitedQuota => isPortuguese ? 'Cota limitada' : 'Limited quota';
  String get unavailableItems => isPortuguese ? 'Indisponíveis' : 'Unavailable';
  String get commercialAvailability =>
      isPortuguese ? 'Disponibilidade comercial' : 'Commercial availability';
  String get servicePeriod =>
      isPortuguese ? 'Período de serviço' : 'Service period';
  String get channels => isPortuguese ? 'Canais' : 'Channels';
  String get dailyQuota => isPortuguese ? 'Cota do dia' : 'Daily quota';
  String get remaining => isPortuguese ? 'Disponível' : 'Remaining';
  String get searchItem => isPortuguese ? 'Buscar item...' : 'Search item...';
  String get lunch => isPortuguese ? 'Almoço' : 'Lunch';
  String get allDay => isPortuguese ? 'Dia todo' : 'All day';
  String get noMenuItems => isPortuguese
      ? 'Nenhum item publicado para hoje.'
      : 'No items published for today.';
  String get unableToLoadMenu => isPortuguese
      ? 'Não foi possível carregar o menu do dia.'
      : 'Unable to load the daily menu.';
  String get today => isPortuguese ? 'Hoje' : 'Today';
  String get allChannels => isPortuguese ? 'Todos os canais' : 'All channels';
  String get unlimited => isPortuguese ? 'Ilimitada' : 'Unlimited';
  String get soldOut => isPortuguese ? 'Esgotado' : 'Sold out';

  String get smartManagement => isPortuguese
      ? 'Gestão inteligente para pequenas e médias empresas'
      : 'Smart management for small and medium businesses';
  String get email => isPortuguese ? 'Email' : 'Email';
  String get password => isPortuguese ? 'Senha' : 'Password';
  String get rememberAccess => isPortuguese ? 'Lembrar acesso' : 'Remember me';
  String get forgotPassword =>
      isPortuguese ? 'Esqueci minha senha' : 'Forgot password';
  String get signIn => isPortuguese ? 'Entrar' : 'Sign in';
  String get authenticationFailed =>
      isPortuguese ? 'Não foi possível autenticar.' : 'Unable to sign in.';
  String get version => isPortuguese ? 'Versão' : 'Version';
  String get environment => isPortuguese ? 'Ambiente' : 'Environment';
  String get systemNotice =>
      isPortuguese ? 'Informativo do sistema' : 'System notice';
  String get companyNotice =>
      isPortuguese ? 'Informativo da empresa' : 'Company notice';
  String get integratedOperation => isPortuguese
      ? 'Operação integrada em tempo real'
      : 'Real-time integrated operations';
  String get integratedDescription => isPortuguese
      ? 'Acompanhe estoque, vendas, restaurante e financeiro em uma única plataforma preparada para Web, mobile e desktop.'
      : 'Track inventory, sales, restaurant and finance in one platform built for web, mobile and desktop.';
  String get teamNotices =>
      isPortuguese ? 'Comunicados para a equipe' : 'Team announcements';
  String get teamNoticesDescription => isPortuguese
      ? 'Este espaço poderá exibir avisos operacionais, campanhas internas, treinamentos, escala e prioridades do dia.'
      : 'This space can show operational notices, internal campaigns, training, schedules and daily priorities.';
  String get institutionalContent => isPortuguese
      ? 'Imagem ou texto institucional'
      : 'Institutional image or text';
  String get institutionalDescription => isPortuguese
      ? 'Cada empresa poderá personalizar os próximos cards com conteúdo próprio, mantendo a identidade visual do ERP.'
      : 'Each company can customize future cards with its own content while preserving the ERP visual identity.';
  String get modules => isPortuguese ? 'Módulos' : 'Modules';
  String get channel => isPortuguese ? 'Canal' : 'Channel';
  String get status => isPortuguese ? 'Status' : 'Status';
  String get content => isPortuguese ? 'Conteúdo' : 'Content';
  String get visual => isPortuguese ? 'Visual' : 'Visual';
  String get active => isPortuguese ? 'Ativo' : 'Active';
  String get team => isPortuguese ? 'Equipe' : 'Team';
  String get text => isPortuguese ? 'Texto' : 'Text';
  String get image => isPortuguese ? 'Imagem' : 'Image';
  String get forgotPasswordTitle =>
      isPortuguese ? 'Recuperar acesso' : 'Recover access';
  String get forgotPasswordDescription => isPortuguese
      ? 'Informe seu email para iniciar a recuperação de senha quando este serviço estiver disponível.'
      : 'Enter your email to start password recovery when this service is available.';
  String get requestRecovery =>
      isPortuguese ? 'Solicitar recuperação' : 'Request recovery';
  String get recoveryUnavailable => isPortuguese
      ? 'A recuperação de senha ainda não está disponível neste ambiente.'
      : 'Password recovery is not available in this environment yet.';
}
