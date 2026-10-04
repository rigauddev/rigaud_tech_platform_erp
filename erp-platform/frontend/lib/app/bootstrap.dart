import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app.dart';

Future<void> bootstrap() async {
  WidgetsFlutterBinding.ensureInitialized();

  ErrorWidget.builder = (details) => const Directionality(
    textDirection: TextDirection.ltr,
    child: ColoredBox(
      color: Color(0xFFF8FAFC),
      child: Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Text(
            'Não foi possível abrir esta tela. Atualize a página e tente novamente.',
            textAlign: TextAlign.center,
          ),
        ),
      ),
    ),
  );

  runApp(const ProviderScope(child: RigaudTechErpApp()));
}
