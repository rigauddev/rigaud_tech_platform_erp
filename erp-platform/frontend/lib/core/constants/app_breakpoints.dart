import 'package:responsive_framework/responsive_framework.dart';

class AppBreakpoints {
  const AppBreakpoints._();

  static const double mobile = 0;
  static const double tablet = 600;
  static const double desktop = 1024;
  static const double largeDesktop = 1440;

  static const values = [
    Breakpoint(start: mobile, end: tablet - 1, name: MOBILE),
    Breakpoint(start: tablet, end: desktop - 1, name: TABLET),
    Breakpoint(start: desktop, end: largeDesktop - 1, name: DESKTOP),
    Breakpoint(
      start: largeDesktop,
      end: double.infinity,
      name: 'LARGE_DESKTOP',
    ),
  ];
}
