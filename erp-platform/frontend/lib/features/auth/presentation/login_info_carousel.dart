import 'package:flutter/material.dart';

import '../../../app/theme/app_spacing.dart';

final loginInfoItemsCount = _loginInfoItems.length;

class LoginCardShell extends StatelessWidget {
  const LoginCardShell({required this.child, super.key});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.92),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0E2A5A).withValues(alpha: 0.16),
            blurRadius: 32,
            offset: const Offset(0, 20),
          ),
        ],
      ),
      child: child,
    );
  }
}

class LoginInfoCarousel extends StatelessWidget {
  const LoginInfoCarousel({
    required this.controller,
    required this.currentPage,
    required this.onPageChanged,
    super.key,
  });

  final PageController controller;
  final int currentPage;
  final ValueChanged<int> onPageChanged;

  @override
  Widget build(BuildContext context) {
    return LoginCardShell(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: PageView.builder(
                controller: controller,
                itemCount: _loginInfoItems.length,
                onPageChanged: onPageChanged,
                itemBuilder: (context, index) {
                  return _LoginInfoPage(item: _loginInfoItems[index]);
                },
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                for (var index = 0; index < _loginInfoItems.length; index++)
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 220),
                    width: currentPage == index ? 26 : 8,
                    height: 8,
                    margin: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.xxs,
                    ),
                    decoration: BoxDecoration(
                      color: currentPage == index
                          ? const Color(0xFF1777D3)
                          : const Color(0xFFD0D5DD),
                      borderRadius: BorderRadius.circular(999),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _LoginInfoItem {
  const _LoginInfoItem({
    required this.badge,
    required this.title,
    required this.description,
    required this.icon,
    required this.metrics,
  });

  final String badge;
  final String title;
  final String description;
  final IconData icon;
  final List<_LoginMetric> metrics;
}

class _LoginMetric {
  const _LoginMetric({
    required this.label,
    required this.value,
    required this.icon,
  });

  final String label;
  final String value;
  final IconData icon;
}

const _loginInfoItems = [
  _LoginInfoItem(
    badge: 'Informativo do sistema',
    title: 'Operação integrada em tempo real',
    description:
        'Acompanhe estoque, vendas, restaurante e financeiro em uma única plataforma preparada para Web, mobile e desktop.',
    icon: Icons.dashboard_customize_outlined,
    metrics: [
      _LoginMetric(label: 'Módulos', value: 'ERP', icon: Icons.hub_outlined),
      _LoginMetric(
        label: 'Ambiente',
        value: 'Cloud',
        icon: Icons.cloud_outlined,
      ),
    ],
  ),
  _LoginInfoItem(
    badge: 'Informativo da empresa',
    title: 'Comunicados para a equipe',
    description:
        'Este espaço poderá exibir avisos operacionais, campanhas internas, treinamentos, escala e prioridades do dia.',
    icon: Icons.campaign_outlined,
    metrics: [
      _LoginMetric(
        label: 'Canal',
        value: 'Equipe',
        icon: Icons.groups_outlined,
      ),
      _LoginMetric(
        label: 'Status',
        value: 'Ativo',
        icon: Icons.verified_outlined,
      ),
    ],
  ),
  _LoginInfoItem(
    badge: 'Informativo da empresa',
    title: 'Imagem ou texto institucional',
    description:
        'Cada empresa poderá personalizar os próximos cards com conteúdo próprio, mantendo a identidade visual do ERP.',
    icon: Icons.image_outlined,
    metrics: [
      _LoginMetric(
        label: 'Conteúdo',
        value: 'Texto',
        icon: Icons.article_outlined,
      ),
      _LoginMetric(
        label: 'Visual',
        value: 'Imagem',
        icon: Icons.photo_library_outlined,
      ),
    ],
  ),
];

class _LoginInfoPage extends StatelessWidget {
  const _LoginInfoPage({required this.item});

  final _LoginInfoItem item;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.sm,
            vertical: AppSpacing.xs,
          ),
          decoration: BoxDecoration(
            color: const Color(0xFFEAF7FF),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: const Color(0xFFB8EAFA)),
          ),
          child: Text(
            item.badge,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: textTheme.labelMedium?.copyWith(
              color: const Color(0xFF0E2A5A),
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        const Spacer(),
        Container(
          width: 96,
          height: 96,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF1777D3), Color(0xFF33C7D8)],
            ),
            borderRadius: BorderRadius.circular(8),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF1777D3).withValues(alpha: 0.22),
                blurRadius: 24,
                offset: const Offset(0, 14),
              ),
            ],
          ),
          child: Icon(item.icon, color: Colors.white, size: 44),
        ),
        const SizedBox(height: AppSpacing.xl),
        Text(
          item.title,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: textTheme.headlineSmall?.copyWith(
            color: const Color(0xFF0E2A5A),
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          item.description,
          maxLines: 4,
          overflow: TextOverflow.ellipsis,
          style: textTheme.bodyLarge?.copyWith(
            color: const Color(0xFF344054),
            height: 1.35,
          ),
        ),
        const SizedBox(height: AppSpacing.xl),
        Row(
          children: [
            for (final metric in item.metrics) ...[
              Expanded(child: _LoginMetricTile(metric: metric)),
              if (metric != item.metrics.last)
                const SizedBox(width: AppSpacing.sm),
            ],
          ],
        ),
      ],
    );
  }
}

class _LoginMetricTile extends StatelessWidget {
  const _LoginMetricTile({required this.metric});

  final _LoginMetric metric;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 92,
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FBFF),
        border: Border.all(color: const Color(0xFFE4E7EC)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(metric.icon, color: const Color(0xFF1777D3), size: 24),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  metric.label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: const Color(0xFF667085),
                  ),
                ),
                Text(
                  metric.value,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: const Color(0xFF0E2A5A),
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
