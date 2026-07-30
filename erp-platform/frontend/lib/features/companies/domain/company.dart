enum CompanyStatus {
  active,
  inactive,
  suspended;

  String get label {
    return switch (this) {
      CompanyStatus.active => 'Ativa',
      CompanyStatus.inactive => 'Inativa',
      CompanyStatus.suspended => 'Suspensa',
    };
  }
}

class Company {
  const Company({
    required this.id,
    required this.legalName,
    required this.tradeName,
    required this.document,
    required this.slug,
    required this.code,
    required this.status,
    required this.timezone,
    required this.locale,
    required this.currency,
    required this.isActive,
    this.email,
    this.phone,
  });

  final String id;
  final String legalName;
  final String tradeName;
  final String document;
  final String? email;
  final String? phone;
  final String slug;
  final String code;
  final CompanyStatus status;
  final String timezone;
  final String locale;
  final String currency;
  final bool isActive;

  factory Company.fromJson(Map<String, dynamic> json) {
    return Company(
      id: json['id'] as String? ?? '',
      legalName: json['legal_name'] as String? ?? '',
      tradeName: json['trade_name'] as String? ?? '',
      document: json['document'] as String? ?? '',
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      slug: json['slug'] as String? ?? '',
      code: json['code'] as String? ?? '',
      status: CompanyStatus.values.byName(
        json['status'] as String? ?? 'inactive',
      ),
      timezone: json['timezone'] as String? ?? 'America/Sao_Paulo',
      locale: json['locale'] as String? ?? 'pt-BR',
      currency: json['currency'] as String? ?? 'BRL',
      isActive: json['is_active'] as bool? ?? false,
    );
  }
}
