# Frontend Project Structure

Estrutura do Flutter Starter após a DEV-003.

```text
erp-platform/frontend/lib/
├── main.dart
├── app/
│   ├── app.dart
│   ├── bootstrap.dart
│   ├── config/
│   ├── router/
│   └── theme/
├── core/
│   ├── api/
│   ├── constants/
│   ├── errors/
│   ├── extensions/
│   ├── logging/
│   ├── network/
│   ├── storage/
│   └── utils/
├── shared/
│   ├── components/
│   ├── layouts/
│   ├── models/
│   ├── providers/
│   └── widgets/
└── features/
    ├── auth/
    ├── splash/
    ├── dashboard/
    ├── companies/
    ├── users/
    ├── products/
    ├── inventory/
    ├── restaurant/
    ├── fashion/
    ├── sales/
    ├── finance/
    ├── delivery/
    └── fiscal/
```

Cada feature possui:

```text
data/
domain/
presentation/
README.md
```

Nenhuma regra de negócio foi implementada.
