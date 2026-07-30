# Authentication Overview

Fundação técnica de autenticação da Rigaud Tech Platform ERP.

## Escopo da DEV-005

- Login por `tenant`, `email` e `password`.
- Access token JWT.
- Refresh token opaco armazenado apenas como hash.
- Rotação de refresh token.
- Logout com revogação de sessão.
- Endpoint protegido `/api/v1/auth/me`.
- Contexto de tenant no backend.
- Integração Flutter com repository, controller Riverpod, storage seguro e interceptor Bearer.

O CRUD administrativo de empresas foi implementado na DEV-006 e passou a fornecer a resolução real de tenant.

Usuários completos e permissões de negócio ainda não foram implementados.

## Endpoints

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Swagger disponível em `/docs`.
