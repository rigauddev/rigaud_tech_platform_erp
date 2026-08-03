# Database Migrations

Alembic controla a evolução do schema PostgreSQL.

## Comandos

```bash
make db-current
make db-history
make db-revision name="descricao"
make db-upgrade
make db-downgrade
```

Equivalentes dentro do backend:

```bash
alembic current
alembic history
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

## Configuração

O Alembic usa metadata de `app.database.Base`, URL assíncrona, comparação de tipos, comparação de server defaults e naming convention compartilhada.

## Migration inicial

`0001_database_core` cria somente a extensão PostgreSQL `pgcrypto`.

Nenhuma tabela de negócio ou tabela artificial é criada nesta migration.

## Migrations técnicas relevantes

- `0004_companies`: cria `companies` como raiz do tenant.
- `0005_users`: evolui `auth_users` para usuário funcional.
- `0007_mfa_2fa`: adiciona estruturas técnicas de segundo fator.
- `0008_products`: cria a base de produtos multi-tenant.
- `0009_tenant_context`: cria filiais, memberships e contexto opcional em sessões.
- `0010_saas_foundation`: adiciona fundação SaaS.
- `0011_products_branch_qr`: prepara produtos para filial, QR Code e código de barras.
- `0012_categories`: cria categorias multi-tenant.
- `0013_warehouses`: cria depósitos.
- `0014_warehouse_zones`: cria zonas de depósito.
- `0015_warehouse_locations`: cria localizações físicas.
- `0016_receiving_documents`: cria documentos de recebimento.
- `0017_goods_receipt`: adiciona confirmação física e pendência de put away.
- `0018_putaway`: adiciona Put Away, status `available` e rastreabilidade por `origin_module` e `business_process`.
