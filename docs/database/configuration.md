# Database Configuration

Configuração de banco do backend.

## Variáveis

- `DATABASE_URL`
- `DATABASE_ECHO`
- `DATABASE_POOL_SIZE`
- `DATABASE_MAX_OVERFLOW`
- `DATABASE_POOL_TIMEOUT`
- `DATABASE_POOL_RECYCLE`
- `DATABASE_HEALTH_TIMEOUT_SECONDS`

## Engine assíncrona

A engine é criada uma única vez por processo em `app/database/session.py` usando `create_async_engine`.

Configurações aplicadas:

- `pool_pre_ping`
- pool size configurável
- overflow configurável
- timeout configurável
- recycle configurável
- logs SQL apenas quando `DATABASE_ECHO=true`

## Ciclo de sessão

`get_async_session` fornece sessão para FastAPI.

A dependência não faz commit automático, executa rollback quando ocorre erro e fecha a sessão ao final.

Commits devem ser explícitos na camada de aplicação ou Unit of Work.

## Segurança

Connection strings não devem ser logadas em texto puro.

O `.env.example` usa credenciais locais de desenvolvimento e não deve ser usado em ambientes compartilhados ou produtivos.
