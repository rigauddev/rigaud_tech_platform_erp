import 'package:flutter/material.dart';

extension BuildContextExtensions on BuildContext {
  ThemeData get theme => Theme.of(this);
  ColorScheme get colors => theme.colorScheme;
  TextTheme get textStyles => theme.textTheme;

  bool get isMobile => MediaQuery.sizeOf(this).width < 600;
  bool get isTablet {
    final width = MediaQuery.sizeOf(this).width;
    return width >= 600 && width < 1024;
  }

  bool get isDesktop => MediaQuery.sizeOf(this).width >= 1024;
}
