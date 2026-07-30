# Backend Authentication

## Camadas

- `domain`: entidades técnicas, contratos de repositório e exceções.
- `application`: use cases, token service, password service e normalização de entrada.
- `infrastructure`: modelos SQLAlchemy e repositórios.
- `presentation`: schemas Pydantic, dependencies e router FastAPI.

## Estratégia de Senha

O projeto usa `bcrypt` diretamente, com custo 12 e limite de 72 bytes por senha.

`bcrypt` está fixado abaixo da versão 5 para manter comportamento estável no backend atual.

## Logs de Auditoria

Eventos técnicos são enviados para o logger `audit`:

- `auth.login.success`
- `auth.login.failed`
- `auth.refresh.success`
- `auth.refresh.failed`
- `auth.token.reuse_detected`
- `auth.logout`

## Integração com Empresas

Na DEV-006, a autenticação passou a resolver tenant pela tabela `companies`.

O login aceita slug ou código da empresa.

Empresas inativas ou suspensas bloqueiam novos logins.
