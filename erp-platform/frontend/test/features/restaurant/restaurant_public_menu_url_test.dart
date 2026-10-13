import 'package:flutter_test/flutter_test.dart';
import 'package:rigaud_tech_erp/features/restaurant/domain/restaurant_public_menu_url.dart';

void main() {
  test('creates a public menu link using the browser origin on web', () {
    final uri = restaurantPublicMenuUrl(
      qrCode: 'qr-token',
      publicAppUrl: '',
      browserUri: Uri.parse('https://restaurant.example/#/login'),
      isWeb: true,
    );

    expect(
      uri.toString(),
      'https://restaurant.example/#/restaurant/online-menu?qr_code=qr-token',
    );
  });

  test('uses PUBLIC_APP_URL for desktop QR codes', () {
    final uri = restaurantPublicMenuUrl(
      qrCode: 'qr-token',
      publicAppUrl: 'https://restaurant.example',
      browserUri: Uri.parse('file:///app'),
      isWeb: false,
    );

    expect(
      uri.toString(),
      'https://restaurant.example/#/restaurant/online-menu?qr_code=qr-token',
    );
  });

  test('does not create a link when a desktop public URL is missing', () {
    expect(
      restaurantPublicMenuUrl(
        qrCode: 'qr-token',
        publicAppUrl: '',
        browserUri: Uri.parse('file:///app'),
        isWeb: false,
      ),
      isNull,
    );
  });
}
