import 'package:flutter/material.dart';

import '../../../app/theme/app_spacing.dart';
import '../../../core/localization/app_strings.dart';

const loginInfoItemsCount = 3;

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
    required this.strings,
    super.key,
  });

  final PageController controller;
  final int currentPage;
  final ValueChanged<int> onPageChanged;
  final AppStrings strings;

  @override
  Widget build(BuildContext context) {
    final items = _loginInfoItems(strings);
    return LoginCardShell(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: PageView.builder(
                controller: controller,
                itemCount: items.length,
                onPageChanged: onPageChanged,
                itemBuilder: (context, index) {
                  return _LoginInfoPage(item: items[index]);
                },
              ),
            ),
            const SizedBox(height: AppSpacing.md),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                for (var index = 0; index < items.length; index++)
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

List<_LoginInfoItem> _loginInfoItems(AppStrings strings) => [
  _LoginInfoItem(
    badge: strings.systemNotice,
    title: strings.integratedOperation,
    description: strings.integratedDescription,
    icon: Icons.dashboard_customize_outlined,
    metrics: [
      _LoginMetric(
        label: strings.modules,
        value: 'ERP',
        icon: Icons.hub_outlined,
      ),
      _LoginMetric(
        label: strings.environment,
        value: 'Cloud',
        icon: Icons.cloud_outlined,
      ),
    ],
  ),
  _LoginInfoItem(
    badge: strings.companyNotice,
    title: strings.teamNotices,
    description: strings.teamNoticesDescription,
    icon: Icons.campaign_outlined,
    metrics: [
      _LoginMetric(
        label: strings.channel,
        value: strings.team,
        icon: Icons.groups_outlined,
      ),
      _LoginMetric(
        label: strings.status,
        value: strings.active,
        icon: Icons.verified_outlined,
      ),
    ],
  ),
  _LoginInfoItem(
    badge: strings.companyNotice,
    title: strings.institutionalContent,
    description: strings.institutionalDescription,
    icon: Icons.image_outlined,
    metrics: [
      _LoginMetric(
        label: strings.content,
        value: strings.text,
        icon: Icons.article_outlined,
      ),
      _LoginMetric(
        label: strings.visual,
        value: strings.image,
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
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Align(
          alignment: Alignment.center,
          child: Container(
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
        ),
        Container(
          width: 72,
          height: 72,
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
          child: Icon(item.icon, color: Colors.white, size: 34),
        ),
        const SizedBox(height: AppSpacing.lg),
        Text(
          item.title,
          textAlign: TextAlign.center,
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
          textAlign: TextAlign.center,
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
          style: textTheme.bodyLarge?.copyWith(
            color: const Color(0xFF344054),
            height: 1.35,
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
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
      height: 76,
      padding: const EdgeInsets.all(AppSpacing.sm),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FBFF),
        border: Border.all(color: const Color(0xFFE4E7EC)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(metric.icon, color: const Color(0xFF1777D3), size: 20),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  metric.label,
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: const Color(0xFF667085),
                  ),
                ),
                Text(
                  metric.value,
                  textAlign: TextAlign.center,
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
