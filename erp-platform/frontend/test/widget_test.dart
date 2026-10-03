import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/app.dart';
import 'package:rigaud_tech_erp/app/router/route_guard.dart';
import 'package:rigaud_tech_erp/core/api/api_response.dart';
import 'package:rigaud_tech_erp/features/auth/presentation/login_screen.dart';
import 'package:rigaud_tech_erp/features/not_found/presentation/not_found_screen.dart';
import 'package:rigaud_tech_erp/features/users/domain/user.dart';

void main() {
  testWidgets('abre diretamente na tela de login', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: RigaudTechErpApp()));
    await tester.pumpAndSettle();

    expect(find.text('Rigaud Tech Platform ERP'), findsOneWidget);
    expect(find.text('Continuar'), findsNothing);
  });

  testWidgets('renderiza a tela visual de login', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: LoginScreen())),
    );
    await tester.pump(const Duration(milliseconds: 500));

    expect(find.byType(SingleChildScrollView), findsNothing);
    expect(find.byType(Image), findsOneWidget);
    expect(find.byType(PageView), findsOneWidget);
    expect(find.text('Informativo do sistema'), findsOneWidget);
    expect(find.text('Operação integrada em tempo real'), findsOneWidget);
    expect(find.text('Rigaud Tech Platform ERP'), findsOneWidget);
    expect(
      find.text('Gestão inteligente para pequenas e médias empresas'),
      findsOneWidget,
    );
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Tenant'), findsNothing);
    expect(find.text('Senha'), findsOneWidget);
    expect(find.text('Entrar'), findsOneWidget);
    expect(find.text('Esqueci minha senha'), findsOneWidget);
    expect(find.text('Lembrar acesso'), findsOneWidget);
    expect(find.textContaining('Versão'), findsOneWidget);
    expect(find.textContaining('Ambiente'), findsWidgets);
  });

  testWidgets('renderiza pagina 404 para rota desconhecida', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: NotFoundScreen()));

    expect(find.text('Página não encontrada'), findsOneWidget);
  });

  test('protege o dashboard sem sessao autenticada', () {
    const guard = RouteGuard(
      enabled: true,
      isAuthenticated: false,
      isSuperuser: false,
    );

    expect(guard.redirect('/dashboard'), '/login');
  });

  test('bloqueia rota administrativa de empresas para usuario comum', () {
    const guard = RouteGuard(
      enabled: true,
      isAuthenticated: true,
      isSuperuser: false,
    );

    expect(guard.redirect('/companies'), '/companies/current');
  });

  test('bloqueia rota administrativa de usuarios para usuario comum', () {
    const guard = RouteGuard(
      enabled: true,
      isAuthenticated: true,
      isSuperuser: false,
    );

    expect(guard.redirect('/users'), '/users/me');
    expect(guard.redirect('/users/me'), isNull);
    expect(guard.redirect('/users/me/change-password'), isNull);
  });

  test('bloqueia rota de auditoria para usuario comum', () {
    const guard = RouteGuard(
      enabled: true,
      isAuthenticated: true,
      isSuperuser: false,
    );

    expect(guard.redirect('/audit'), '/users/me');
  });

  test('bloqueia ambiente demo para usuario comum', () {
    const guard = RouteGuard(
      enabled: true,
      isAuthenticated: true,
      isSuperuser: false,
    );

    expect(guard.redirect('/demo'), '/dashboard');
  });

  test('protege rota de categorias sem sessao autenticada', () {
    const guard = RouteGuard(
      enabled: true,
      isAuthenticated: false,
      isSuperuser: false,
    );

    expect(guard.redirect('/categories'), '/login');
  });

  test('permite rota de empresas para superuser', () {
    const guard = RouteGuard(
      enabled: true,
      isAuthenticated: true,
      isSuperuser: true,
    );

    expect(guard.redirect('/companies'), isNull);
  });

  test('desserializa perfil de usuario sem expor credenciais', () {
    final user = UserProfile.fromJson({
      'id': 'user-id',
      'tenant_id': 'company-id',
      'tenant_slug': 'rigaud',
      'email': 'user@example.com',
      'first_name': 'Maria',
      'last_name': 'Rigaud',
      'display_name': null,
      'status': 'active',
      'is_active': true,
      'is_superuser': false,
      'must_change_password': false,
      'last_login_at': null,
    });

    expect(user.title, 'Maria Rigaud');
    expect(user.status, UserStatus.active);
    expect(user.isActive, isTrue);
  });

  test('interpreta envelope padronizado de erro', () {
    final envelope = ApiEnvelope.fromJson({
      'success': false,
      'code': 'USER_NOT_FOUND',
      'message': 'Usuário não encontrado.',
      'request_id': 'request-123',
      'errors': [
        {
          'field': 'email',
          'code': 'INVALID_EMAIL',
          'message': 'Email inválido.',
        },
      ],
    });

    expect(envelope.success, isFalse);
    expect(envelope.requestId, 'request-123');
    expect(envelope.errors?.single.field, 'email');
  });
}
