class DemoStatus {
  const DemoStatus({
    required this.companies,
    required this.branches,
    required this.users,
    required this.categories,
    required this.products,
  });

  factory DemoStatus.fromJson(Map<String, dynamic> json) {
    return DemoStatus(
      companies: json['companies'] as int? ?? 0,
      branches: json['branches'] as int? ?? 0,
      users: json['users'] as int? ?? 0,
      categories: json['categories'] as int? ?? 0,
      products: json['products'] as int? ?? 0,
    );
  }

  final int companies;
  final int branches;
  final int users;
  final int categories;
  final int products;
}
