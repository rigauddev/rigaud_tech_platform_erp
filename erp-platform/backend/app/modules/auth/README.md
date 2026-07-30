# Auth

Módulo técnico de autenticação, autorização futura e segurança de identidade.

## Escopo Atual

- login por tenant, email e senha.
- JWT access token.
- refresh token opaco com hash persistido.
- rotação de refresh token.
- logout com revogação de sessão.
- `/me` protegido.
- logs de auditoria de autenticação.

## Estrutura

- `application`: use cases e serviços técnicos.
- `domain`: entidades, contratos e exceções.
- `infrastructure`: modelos SQLAlchemy e repositórios.
- `presentation`: schemas, dependencies e router FastAPI.
- `tests`: reservado para testes internos do módulo.

Nenhuma regra de negócio do ERP foi implementada.

## DEV-008

Auth usa o contrato padronizado de respostas da API, inclui `request_id` nas respostas e gera eventos de auditoria para login, falhas relevantes, refresh suspeito e logout.

Na DEV-009, Auth passa a oferecer autenticação em dois fatores por TOTP, email, SMS e recovery codes. Detalhes locais:

- `MFA.md`
- `MFA_API.md`
- `MFA_DATABASE.md`
- `MFA_RULES.md`
- `MFA_TESTS.md`
- `MFA_ROADMAP.md`
