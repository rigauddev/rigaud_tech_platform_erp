class CompanyInput {
  const CompanyInput({
    required this.legalName,
    required this.tradeName,
    required this.document,
    required this.slug,
    required this.code,
    this.email,
    this.phone,
    this.timezone = 'America/Sao_Paulo',
    this.locale = 'pt-BR',
    this.currency = 'BRL',
  });

  final String legalName;
  final String tradeName;
  final String document;
  final String? email;
  final String? phone;
  final String slug;
  final String code;
  final String timezone;
  final String locale;
  final String currency;

  Map<String, dynamic> toJson() {
    return {
      'legal_name': legalName,
      'trade_name': tradeName,
      'document': document,
      'email': email,
      'phone': phone,
      'slug': slug,
      'code': code,
      'timezone': timezone,
      'locale': locale,
      'currency': currency,
    };
  }
}
