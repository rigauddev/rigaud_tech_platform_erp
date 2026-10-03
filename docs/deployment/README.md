# Deployment Documentation

Entrada de documentacao de deployment do produto.

DOC-008 define a arquitetura base em `docs/architecture/deployment/README.md`.

DOC-009 define como esse conhecimento sera apresentado para times tecnicos, implantacao, suporte, parceiros e usuarios.

## Cloud

```text
Rigaud Tech Cloud
  ↓
Multi-tenant
  ↓
Empresas
  ↓
Filiais
```

Cloud e o ERP hospedado pela Rigaud Tech ou infraestrutura cloud definida futuramente.

## On-Premise

```text
Servidor dedicado
    ↓
Docker
    ↓
ERP Backend
PostgreSQL
Redis
Nginx
Sync Engine futuro
    ↓
Rede local
    ↓
Computadores / celulares / tablets
```

O servidor On-Premise nao deve pressupor MacBook ou computador de usuario como servidor.

Servidor de producao recomendado: Linux.

## Offline

Com internet:

```text
Internet disponível
    ↓
Cloud / servidor
    ↕
Sincronização futura
    ↕
Dispositivos
```

Sem internet:

```text
Internet indisponível
    ↓
Cliente continua trabalhando
    ↓
Dados locais/eventos pendentes
    ↓
Internet retorna
    ↓
Sync Engine futuro
    ↓
Reconciliação
```

## Limite Atual

Sync Engine, Offline-First completo e reconciliacao automatica nao sao implementados nesta task.
