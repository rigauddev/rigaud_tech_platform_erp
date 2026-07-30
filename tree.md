# Estrutura do Workspace

```text
Rigaud Tech Platform ERP/
├── .dockerignore
├── .env.example
├── CHANGELOG.md
├── Makefile
├── README.md
├── docker-compose.yml
├── docker/
│   ├── backend/
│   │   └── Dockerfile
│   ├── flutter/
│   │   └── Dockerfile
│   └── nginx/
│       └── default.conf
├── docs/
│   ├── README.md
│   ├── backend/
│   │   ├── README.md
│   │   └── backend-starter.md
│   ├── development/
│   │   ├── README.md
│   │   └── docker.md
│   └── frontend/
│       ├── README.md
│       └── flutter-starter.md
├── erp-blueprint/
│   ├── 000-master-prompt.md
│   ├── README.md
│   ├── docs/
│   │   ├── README.md
│   │   ├── academy/
│   │   │   └── README.md
│   │   ├── adr/
│   │   │   └── README.md
│   │   ├── architecture/
│   │   │   └── README.md
│   │   ├── backlog/
│   │   │   └── README.md
│   │   ├── index.md
│   │   ├── modules/
│   │   │   └── README.md
│   │   ├── prompts/
│   │   │   └── README.md
│   │   ├── research/
│   │   │   └── README.md
│   │   ├── roadmap/
│   │   │   └── README.md
│   │   └── templates/
│   │       └── README.md
│   └── mkdocs.yml
├── erp-platform/
│   ├── README.md
│   ├── backend/
│   │   ├── .env.example
│   │   ├── .env.local.example
│   │   ├── .env.production.example
│   │   ├── .env.test.example
│   │   ├── .gitignore
│   │   ├── README.md
│   │   ├── alembic.ini
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── api/
│   │   │   │   ├── README.md
│   │   │   │   ├── __init__.py
│   │   │   │   └── v1/
│   │   │   │       ├── README.md
│   │   │   │       ├── __init__.py
│   │   │   │       ├── router.py
│   │   │   │       └── routes/
│   │   │   │           ├── __init__.py
│   │   │   │           └── health.py
│   │   │   ├── core/
│   │   │   │   ├── README.md
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── logging.py
│   │   │   │   ├── openapi.py
│   │   │   │   └── security.py
│   │   │   ├── db/
│   │   │   │   ├── README.md
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   └── session.py
│   │   │   ├── logs/
│   │   │   │   └── .gitkeep
│   │   │   ├── main.py
│   │   │   ├── modules/
│   │   │   │   ├── .gitkeep
│   │   │   │   └── README.md
│   │   │   └── shared/
│   │   │       ├── README.md
│   │   │       ├── __init__.py
│   │   │       ├── application/
│   │   │       │   ├── README.md
│   │   │       │   ├── __init__.py
│   │   │       │   └── use_case.py
│   │   │       ├── domain/
│   │   │       │   ├── README.md
│   │   │       │   ├── __init__.py
│   │   │       │   └── repository.py
│   │   │       ├── infrastructure/
│   │   │       │   ├── README.md
│   │   │       │   └── __init__.py
│   │   │       └── presentation/
│   │   │           ├── README.md
│   │   │           ├── __init__.py
│   │   │           └── schemas.py
│   │   ├── docker/
│   │   │   ├── .gitkeep
│   │   │   └── README.md
│   │   ├── migrations/
│   │   │   ├── README.md
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/
│   │   │       └── .gitkeep
│   │   ├── pyproject.toml
│   │   └── tests/
│   │       └── README.md
│   └── frontend/
│       ├── .gitignore
│       ├── README.md
│       ├── analysis_options.yaml
│       ├── android/
│       ├── ios/
│       ├── lib/
│       │   ├── app.dart
│       │   ├── config/
│       │   │   ├── router/
│       │   │   │   ├── app_router.dart
│       │   │   │   └── app_routes.dart
│       │   │   └── theme/
│       │   │       └── app_theme.dart
│       │   ├── core/
│       │   │   ├── network/
│       │   │   │   └── dio_client.dart
│       │   │   ├── responsive/
│       │   │   │   └── app_breakpoints.dart
│       │   │   └── state/
│       │   │       ├── view_state.dart
│       │   │       └── view_state.freezed.dart
│       │   ├── features/
│       │   │   ├── login/
│       │   │   │   ├── view/
│       │   │   │   │   └── login_page.dart
│       │   │   │   └── view_model/
│       │   │   │       └── login_view_model.dart
│       │   │   └── splash/
│       │   │       ├── view/
│       │   │       │   └── splash_page.dart
│       │   │       └── view_model/
│       │   │           └── splash_view_model.dart
│       │   ├── main.dart
│       │   └── shared/
│       │       └── widgets/
│       ├── linux/
│       ├── macos/
│       ├── pubspec.lock
│       ├── pubspec.yaml
│       ├── rigaud_tech_erp.iml
│       ├── test/
│       │   └── widget_test.dart
│       ├── web/
│       └── windows/
├── scripts/
│   └── README.md
└── tree.md
```
