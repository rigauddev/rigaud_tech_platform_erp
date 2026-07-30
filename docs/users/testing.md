# Users Testing

## Backend

```bash
docker compose exec -T backend pytest tests/unit/users tests/integration/users -q
docker compose exec -T backend pytest -q
```

## Flutter

```bash
docker compose exec -T frontend flutter analyze
docker compose exec -T frontend flutter test
docker compose exec -T frontend flutter build web
```

## Plataformas

Web é validada por build.
macOS e iOS devem ser validados em host macOS com Xcode configurado.
Android deve ser validado com SDK/emulador configurado.
Windows deve ser validado em host Windows.

## Validação DEV-007

Em 2026-07-29:

- Web: `flutter build web` validado com sucesso no container.
- macOS: `flutter run -d macos --no-pub` iniciou build, mas o CodeSign falhou por atributos estendidos do File Provider no bundle gerado.
- iOS: simulador `iPhone 16 Pro Max` disponível e iniciado; build falhou no CodeSign do host.
- Android: AVD `Pixel_9_Pro_XL` disponível, mas `flutter doctor` aponta licenças Android pendentes.
- Windows: não validado neste host macOS.
