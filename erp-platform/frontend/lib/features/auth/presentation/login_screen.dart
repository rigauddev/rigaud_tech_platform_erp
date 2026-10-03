import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/config/app_config.dart';
import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../core/api/api_error.dart';
import '../../../core/localization/app_language.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_text_field.dart';
import '../domain/auth_state.dart';
import 'auth_controller.dart';
import 'login_info_carousel.dart';

final rememberAccessProvider = NotifierProvider<RememberAccessNotifier, bool>(
  RememberAccessNotifier.new,
);

class RememberAccessNotifier extends Notifier<bool> {
  @override
  bool build() => false;

  void update(bool value) {
    state = value;
  }
}

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  static const _appVersion = String.fromEnvironment(
    'APP_VERSION',
    defaultValue: '0.1.0',
  );
  static const _buildNumber = String.fromEnvironment(
    'BUILD_NUMBER',
    defaultValue: 'dev',
  );

  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _carouselController = PageController();
  Timer? _carouselTimer;
  int _currentInfoPage = 0;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _carouselTimer = Timer.periodic(const Duration(seconds: 6), (_) {
      if (!mounted || !_carouselController.hasClients) {
        return;
      }
      final nextPage = (_currentInfoPage + 1) % loginInfoItemsCount;
      _carouselController.animateToPage(
        nextPage,
        duration: const Duration(milliseconds: 420),
        curve: Curves.easeOutCubic,
      );
    });
  }

  @override
  void dispose() {
    _carouselTimer?.cancel();
    _carouselController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final config = AppConfig.fromEnvironment();
    final rememberAccess = ref.watch(rememberAccessProvider);
    final authState = ref.watch(authControllerProvider);
    final strings = ref.watch(appStringsProvider);

    ref.listen(authControllerProvider, (previous, next) {
      final isAuthenticated = next.value?.isAuthenticated ?? false;
      if (isAuthenticated && mounted) {
        context.go(AppRoutes.dashboard);
      }
      final requiresMfa = next.value?.requiresMfa ?? false;
      if (requiresMfa && mounted) {
        context.go(AppRoutes.mfaVerify);
      }
    });

    final keyboardInset = MediaQuery.viewInsetsOf(context).bottom;

    return Scaffold(
      resizeToAvoidBottomInset: false,
      body: Stack(
        fit: StackFit.expand,
        children: [
          _LoginBackground(strings: strings),
          SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) {
                final isCompact = constraints.maxWidth < 700;
                final cardWidth = isCompact ? 360.0 : 400.0;
                final cardHeight = isCompact ? 640.0 : 620.0;
                return AnimatedPadding(
                  duration: const Duration(milliseconds: 220),
                  curve: Curves.easeOutCubic,
                  padding: EdgeInsets.fromLTRB(
                    isCompact ? AppSpacing.md : AppSpacing.xxl,
                    AppSpacing.md,
                    isCompact ? AppSpacing.md : AppSpacing.xxl,
                    keyboardInset > 0 ? keyboardInset * 0.52 : AppSpacing.md,
                  ),
                  child: Column(
                    children: [
                      Expanded(
                        child: Align(
                          alignment: Alignment.center,
                          child: FittedBox(
                            fit: BoxFit.scaleDown,
                            child: isCompact
                                ? SizedBox(
                                    width: cardWidth,
                                    height: cardHeight,
                                    child: _LoginForm(
                                      emailController: _emailController,
                                      passwordController: _passwordController,
                                      rememberAccess: rememberAccess,
                                      authState: authState,
                                      isSubmitting: _isSubmitting,
                                      strings: strings,
                                      onRememberChanged: (value) {
                                        ref
                                            .read(
                                              rememberAccessProvider.notifier,
                                            )
                                            .update(value ?? false);
                                      },
                                      onSubmit: _submit,
                                    ),
                                  )
                                : Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      SizedBox(
                                        width: cardWidth,
                                        height: cardHeight,
                                        child: LoginInfoCarousel(
                                          controller: _carouselController,
                                          currentPage: _currentInfoPage,
                                          onPageChanged: (page) {
                                            setState(() {
                                              _currentInfoPage = page;
                                            });
                                          },
                                          strings: strings,
                                        ),
                                      ),
                                      const SizedBox(width: AppSpacing.lg),
                                      SizedBox(
                                        width: cardWidth,
                                        height: cardHeight,
                                        child: _LoginForm(
                                          emailController: _emailController,
                                          passwordController:
                                              _passwordController,
                                          rememberAccess: rememberAccess,
                                          authState: authState,
                                          isSubmitting: _isSubmitting,
                                          strings: strings,
                                          onRememberChanged: (value) {
                                            ref
                                                .read(
                                                  rememberAccessProvider
                                                      .notifier,
                                                )
                                                .update(value ?? false);
                                          },
                                          onSubmit: _submit,
                                        ),
                                      ),
                                    ],
                                  ),
                          ),
                        ),
                      ),
                      _LoginFooter(
                        version: _appVersion,
                        buildNumber: _buildNumber,
                        api: config.apiBaseUrl,
                        environment: config.environment.name,
                        strings: strings,
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
          Positioned(
            top: AppSpacing.md,
            right: AppSpacing.md,
            child: _LanguageSelector(
              language: ref.watch(appLanguageProvider),
              onSelected: (language) {
                ref.read(appLanguageProvider.notifier).select(language);
              },
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _submit() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text;
    if (email.isEmpty || password.isEmpty) {
      return;
    }

    setState(() => _isSubmitting = true);
    await ref
        .read(authControllerProvider.notifier)
        .login(email: email, password: password);
    if (mounted) {
      setState(() => _isSubmitting = false);
    }
  }
}

class _LoginBackground extends StatelessWidget {
  const _LoginBackground({required this.strings});

  final AppStrings strings;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final isCompact = width < 700;

    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFEFFBFF), Color(0xFFF7FAFC), Color(0xFFEAF2FF)],
        ),
      ),
      child: Stack(
        fit: StackFit.expand,
        children: [
          CustomPaint(painter: _LoginGridPainter()),
          Positioned(
            left: isCompact ? -90 : 64,
            top: isCompact ? 44 : 88,
            child: _CloudMark(size: isCompact ? 172 : 260),
          ),
          Positioned(
            right: isCompact ? -72 : 80,
            bottom: isCompact ? 96 : 80,
            child: _ModuleConstellation(size: isCompact ? 210 : 320),
          ),
          if (!isCompact) ...[
            Positioned(
              left: 84,
              bottom: 104,
              child: _InsightPanel(
                icon: Icons.point_of_sale_outlined,
                title: strings.isPortuguese ? 'Vendas' : 'Sales',
                value: '+18%',
              ),
            ),
            Positioned(
              left: 164,
              top: 246,
              child: _InsightPanel(
                icon: Icons.inventory_2_outlined,
                title: strings.inventory,
                value: 'Cloud',
              ),
            ),
            Positioned(
              right: 118,
              top: 118,
              child: _InsightPanel(
                icon: Icons.restaurant_menu_outlined,
                title: strings.isPortuguese ? 'Restaurante' : 'Restaurant',
                value: 'Online',
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _LoginGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final linePaint = Paint()
      ..color = const Color(0xFF0E2A5A).withValues(alpha: 0.055)
      ..strokeWidth = 1;
    const gap = 44.0;

    for (double x = 0; x < size.width; x += gap) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), linePaint);
    }
    for (double y = 0; y < size.height; y += gap) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), linePaint);
    }

    final pathPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..color = const Color(0xFF33C7D8).withValues(alpha: 0.16);
    final path = Path()
      ..moveTo(size.width * 0.05, size.height * 0.74)
      ..cubicTo(
        size.width * 0.24,
        size.height * 0.50,
        size.width * 0.48,
        size.height * 0.82,
        size.width * 0.68,
        size.height * 0.58,
      )
      ..cubicTo(
        size.width * 0.80,
        size.height * 0.44,
        size.width * 0.90,
        size.height * 0.28,
        size.width * 1.02,
        size.height * 0.36,
      );
    canvas.drawPath(path, pathPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _CloudMark extends StatelessWidget {
  const _CloudMark({required this.size});

  final double size;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: 0.24,
      child: SizedBox(
        width: size,
        height: size * 0.72,
        child: Stack(
          children: [
            Positioned(
              left: size * 0.08,
              top: size * 0.18,
              child: Icon(
                Icons.hub_outlined,
                size: size * 0.5,
                color: const Color(0xFF1777D3),
              ),
            ),
            Positioned(
              right: 0,
              bottom: 0,
              child: Icon(
                Icons.cloud_outlined,
                size: size * 0.64,
                color: const Color(0xFF33C7D8),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ModuleConstellation extends StatelessWidget {
  const _ModuleConstellation({required this.size});

  final double size;

  @override
  Widget build(BuildContext context) {
    final color = const Color(0xFF0E2A5A).withValues(alpha: 0.12);
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        children: [
          _ModuleNode(
            alignment: const Alignment(-0.72, -0.42),
            icon: Icons.storefront_outlined,
            color: color,
          ),
          _ModuleNode(
            alignment: const Alignment(0.52, -0.56),
            icon: Icons.analytics_outlined,
            color: color,
          ),
          _ModuleNode(
            alignment: const Alignment(-0.22, 0.28),
            icon: Icons.inventory_outlined,
            color: color,
          ),
          _ModuleNode(
            alignment: const Alignment(0.62, 0.42),
            icon: Icons.devices_outlined,
            color: color,
          ),
        ],
      ),
    );
  }
}

class _ModuleNode extends StatelessWidget {
  const _ModuleNode({
    required this.alignment,
    required this.icon,
    required this.color,
  });

  final Alignment alignment;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: alignment,
      child: Container(
        width: 70,
        height: 70,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.72),
          border: Border.all(color: color),
          borderRadius: BorderRadius.circular(14),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF0E2A5A).withValues(alpha: 0.07),
              blurRadius: 24,
              offset: const Offset(0, 12),
            ),
          ],
        ),
        child: Icon(icon, color: const Color(0xFF1777D3)),
      ),
    );
  }
}

class _InsightPanel extends StatelessWidget {
  const _InsightPanel({
    required this.icon,
    required this.title,
    required this.value,
  });

  final IconData icon;
  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 148,
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.72),
        border: Border.all(color: Colors.white),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0E2A5A).withValues(alpha: 0.08),
            blurRadius: 22,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF1777D3), size: 24),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.labelMedium,
                ),
                Text(
                  value,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LoginForm extends StatelessWidget {
  const _LoginForm({
    required this.emailController,
    required this.passwordController,
    required this.rememberAccess,
    required this.authState,
    required this.isSubmitting,
    required this.strings,
    required this.onRememberChanged,
    required this.onSubmit,
  });

  final TextEditingController emailController;
  final TextEditingController passwordController;
  final bool rememberAccess;
  final AsyncValue<AuthState> authState;
  final bool isSubmitting;
  final AppStrings strings;
  final ValueChanged<bool?> onRememberChanged;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final error = authState.error;
    final errorMessage = switch (error) {
      ApiError(message: final message) => message,
      Object() => strings.authenticationFailed,
      null => null,
    };

    return LoginCardShell(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const _BrandLogo(),
            const SizedBox(height: AppSpacing.md),
            Text(
              strings.appName,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: const Color(0xFF0E2A5A),
              ),
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              strings.smartManagement,
              textAlign: TextAlign.center,
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: const Color(0xFF344054)),
            ),
            const SizedBox(height: AppSpacing.xl),
            AppTextField(
              controller: emailController,
              label: strings.email,
              keyboardType: TextInputType.emailAddress,
              prefixIcon: Icons.email_outlined,
            ),
            const SizedBox(height: AppSpacing.md),
            AppTextField(
              controller: passwordController,
              label: strings.password,
              obscureText: true,
              prefixIcon: Icons.lock_outline,
            ),
            if (errorMessage != null) ...[
              const SizedBox(height: AppSpacing.sm),
              Text(errorMessage, style: TextStyle(color: colorScheme.error)),
            ],
            const SizedBox(height: AppSpacing.sm),
            Row(
              children: [
                Checkbox(value: rememberAccess, onChanged: onRememberChanged),
                Expanded(
                  child: Text(
                    strings.rememberAccess,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Flexible(
                  child: TextButton(
                    onPressed: () => context.go(AppRoutes.forgotPassword),
                    child: Text(
                      strings.forgotPassword,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.md),
            AppButton(
              label: strings.signIn,
              icon: Icons.login,
              isLoading: isSubmitting,
              onPressed: onSubmit,
            ),
          ],
        ),
      ),
    );
  }
}

class _BrandLogo extends StatelessWidget {
  const _BrandLogo();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 104,
      child: Image.asset(
        'assets/images/rigaud-tech-logo.png',
        fit: BoxFit.contain,
        alignment: Alignment.center,
        filterQuality: FilterQuality.high,
        semanticLabel: 'Rigaud Tech',
        errorBuilder: (context, error, stackTrace) {
          return Icon(
            Icons.business_outlined,
            size: 64,
            color: Theme.of(context).colorScheme.primary,
          );
        },
      ),
    );
  }
}

class _LoginFooter extends StatelessWidget {
  const _LoginFooter({
    required this.version,
    required this.buildNumber,
    required this.api,
    required this.environment,
    required this.strings,
  });

  final String version;
  final String buildNumber;
  final String api;
  final String environment;
  final AppStrings strings;

  @override
  Widget build(BuildContext context) {
    final style = Theme.of(context).textTheme.labelSmall?.copyWith(
      color: const Color(0xFF344054),
      fontWeight: FontWeight.w600,
    );
    final items = [
      '${strings.version} $version',
      'Build $buildNumber',
      'API $api',
      '${strings.environment} $environment',
    ];

    return Wrap(
      alignment: WrapAlignment.center,
      spacing: AppSpacing.md,
      runSpacing: AppSpacing.xs,
      children: [
        for (final item in items)
          Text(
            item,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: style,
          ),
      ],
    );
  }
}

class _LanguageSelector extends StatelessWidget {
  const _LanguageSelector({required this.language, required this.onSelected});

  final AppLanguage language;
  final ValueChanged<AppLanguage> onSelected;

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<AppLanguage>(
      tooltip: 'Selecionar idioma',
      onSelected: onSelected,
      itemBuilder: (context) => [
        for (final item in AppLanguage.values)
          CheckedPopupMenuItem<AppLanguage>(
            value: item,
            checked: item == language,
            child: Text(
              '${item == AppLanguage.portuguese ? '🇧🇷' : '🇺🇸'}  ${item.label}',
            ),
          ),
      ],
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: .9),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          language == AppLanguage.portuguese ? '🇧🇷  PT' : '🇺🇸  EN',
        ),
      ),
    );
  }
}
