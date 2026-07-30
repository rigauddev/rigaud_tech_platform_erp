# Users

Módulo de Usuários da Rigaud Tech Platform ERP.

Na DEV-007, o usuário oficial continua sendo o usuário autenticável existente em `auth_users`.
O módulo Users evolui essa tabela com perfil, status funcional e operações administrativas.

## Camadas

- `domain`: status, exceptions e contrato de repositório.
- `application`: validações e use cases.
- `infrastructure`: repository SQLAlchemy sobre `AuthUserModel`.
- `presentation`: schemas e router FastAPI.
- `tests`: reservado para testes internos do módulo.

## Regras Principais

- `User.tenant_id = Company.id`.
- Email é normalizado em lowercase.
- Email é único por empresa, mas pode existir em empresas diferentes.
- `status` é a fonte funcional de verdade.
- `is_active` permanece como compatibilidade derivada de `status`.
- Apenas superusuários administram usuários nesta etapa.
- Usuários comuns acessam apenas perfil próprio e troca de senha própria.

## DEV-008

Users usa respostas padronizadas e registra eventos de auditoria em criação, alteração, status, troca de senha e reset de senha.
