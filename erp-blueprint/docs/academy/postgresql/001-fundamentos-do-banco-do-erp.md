# Fundamentos do Banco do ERP

PostgreSQL é o banco relacional principal da Rigaud Tech Platform ERP.

## Conceitos

Tabelas organizam dados em colunas. Registros são linhas dentro dessas tabelas.

A chave primária identifica um registro de forma única.

UUID é um identificador não sequencial, útil em sistemas distribuídos.

Chave estrangeira conecta registros de tabelas diferentes.

Índices ajudam o banco a localizar dados com mais eficiência.

## Transactions

Uma transaction agrupa operações.

`commit` confirma mudanças.

`rollback` desfaz mudanças quando há erro.

## Migrations e SQLAlchemy

Migrations versionam alterações de schema.

SQLAlchemy é a camada Python usada para mapear modelos e executar operações no banco.

A sessão SQLAlchemy representa uma unidade de trabalho com o banco.

## Multi-tenancy e soft delete

No MVP, dados de empresas serão separados por `tenant_id` em um PostgreSQL compartilhado.

Soft delete marca um registro como excluído usando `deleted_at`, sem remover a linha imediatamente.

## Backup e restore

Backup é uma cópia recuperável dos dados.

Restore é o processo de recuperar dados a partir de um backup.

Volume Docker preserva dados em desenvolvimento, mas não substitui backup.

## SaaS e on-premises

No SaaS, usuários acessam a API e o banco central.

No on-premises, a instalação terá um servidor PostgreSQL central da instalação.

Esta aula traz conceitos técnicos e não cria funcionalidades do ERP.
