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
