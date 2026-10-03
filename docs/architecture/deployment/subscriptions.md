# Subscriptions And Entitlements

DOC-008 relaciona distribuicao com a fundacao SaaS prevista na DEV-011.

## Modelo

```text
Subscription
  ↓
Entitlements
  ↓
Modules
  ↓
Feature Flags
```

## Estados Futuros

- `ACTIVE`;
- `PAST_DUE`;
- `GRACE_PERIOD`;
- `SUSPENDED`;
- `CANCELLED`.

## Regras

- inadimplencia nunca apaga dados automaticamente;
- suspensao bloqueia acesso conforme politica comercial;
- dados permanecem preservados;
- billing real continua fora do escopo desta task;
- modulos comerciais nao devem conhecer detalhes do billing provider.

## On-Premise

Instalacoes On-Premise devem ser preparadas para entitlements com tolerancia a indisponibilidade de internet, respeitando auditoria e politica comercial futura.
