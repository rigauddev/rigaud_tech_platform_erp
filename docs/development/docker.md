# Docker Development Environment

Infraestrutura Docker de desenvolvimento da Rigaud Tech Platform ERP.

## Objetivo

Permitir que qualquer desenvolvedor suba todo o ambiente local com:

```bash
make up
```

O comando executa um preflight antes do build, validando:

- Docker daemon acessível.
- `docker compose` válido.
- espaço livre mínimo em disco.

Por padrão, o mínimo exigido é `20000 MB`, porque a imagem Flutter Web é grande. Para ambientes controlados, o limite pode ser sobrescrito:

```bash
MIN_FREE_MB=10000 make up
```

O `make up` também usa `docker compose up --wait` para aguardar os healthchecks. O timeout padrão é `240` segundos e pode ser sobrescrito:

```bash
WAIT_TIMEOUT=360 make up
```

## Stack

- Backend: Python 3.13 e FastAPI
- Banco: PostgreSQL 16
- Cache: Redis
- Frontend: Flutter Web
- Ferramentas: PgAdmin, Mailpit e Nginx

## Arquivos

- `docker-compose.yml`
- `docker/backend/Dockerfile`
- `docker/flutter/Dockerfile`
- `docker/nginx/default.conf`
- `Makefile`
- `.env.example`

## Serviços

- `backend`
- `frontend`
- `postgres`
- `redis`
- `mailpit`
- `pgadmin`
- `nginx`

Todos os serviços usam a network `erp-network`.

Todos os serviços possuem healthcheck configurado.

## Volumes

- `postgres_data`: dados do PostgreSQL.
- `postgres_backups`: diretório reservado para backups futuros.
- `redis_data`: dados do Redis.
- `pgadmin_data`: dados do PgAdmin.
- `flutter_pub_cache`: cache de dependências Flutter/Dart.

## Comandos

```bash
make up
make down
make restart
make logs
make backend
make flutter
make shell-backend
make shell-db
make lint
make format
make test
```

## URLs

- Nginx: `http://localhost:8080`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Frontend Flutter Web: `http://localhost:3000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Mailpit: `http://localhost:8025`
- PgAdmin: `http://localhost:5050`

## Proxy Reverso

- `/api` encaminha para o backend.
- `/` encaminha para o frontend Flutter Web.
- `/nginx-health` valida a saúde interna do Nginx para o `docker compose --wait`.

## Banco

O PostgreSQL usa volume persistente e possui um volume dedicado para backups futuros.

Esta task não cria tabelas nem migrations.

## Seguranca

As credenciais em `.env.example` são apenas para desenvolvimento local.

Antes de qualquer ambiente compartilhado ou produtivo, altere senhas, segredos JWT e políticas de exposição de portas.

## Revisao

Após revisão da DEV-001:

- A configuração Docker foi centralizada na raiz do workspace.
- Dockerfiles duplicados antigos foram removidos.
- O healthcheck do frontend passou a verificar a porta do servidor Flutter Web.
- O Redis passou a usar AOF para persistência local.
- A variável legada `FLUTTER_WEB_PORT` foi removida.
- O Dockerfile Flutter passou a executar como usuário `ubuntu`, evitando uso de Flutter como root.
- O `make up` passou a aguardar healthchecks com `--wait`.
- A imagem Flutter foi fixada em `ghcr.io/cirruslabs/flutter:3.41.9` para evitar que a tag móvel `stable` quebre o ambiente.
- O container Flutter corrige a permissão do cache Pub no startup e executa o processo Flutter como `ubuntu`.
- O healthcheck do Nginx passou a usar `/nginx-health`, evitando falhas por dependência do proxy do frontend.

## Observações

Esta documentação cobre apenas a infraestrutura Docker de desenvolvimento.

Nenhuma funcionalidade, entidade, tela ou regra de negócio do ERP foi implementada nesta task.
