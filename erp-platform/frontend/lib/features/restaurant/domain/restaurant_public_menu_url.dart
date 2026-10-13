Uri? restaurantPublicMenuUrl({
  required String qrCode,
  required String publicAppUrl,
  required Uri browserUri,
  required bool isWeb,
}) {
  if (qrCode.isEmpty) {
    return null;
  }

  final configuredUri = publicAppUrl.trim().isEmpty
      ? null
      : Uri.tryParse(publicAppUrl.trim());
  final baseUri = configuredUri ?? (isWeb ? browserUri : null);
  if (baseUri == null ||
      !baseUri.hasAuthority ||
      baseUri.userInfo.isNotEmpty ||
      !{'http', 'https'}.contains(baseUri.scheme)) {
    return null;
  }

  final basePath = baseUri.path.isEmpty ? '/' : baseUri.path;
  return Uri.parse(
    '${baseUri.scheme}://${baseUri.authority}$basePath'
    '#/restaurant/online-menu?qr_code=${Uri.encodeQueryComponent(qrCode)}',
  );
}
