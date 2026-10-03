# Offline Strategy

DOC-008 define tres niveis de operacao.

## Nivel 1: Internet Disponivel

```text
Cliente -> Rigaud Cloud
```

Uso normal do SaaS.

## Nivel 2: Internet Indisponivel, Rede Local Disponivel

```text
Cliente -> Servidor On-Premise
```

O ERP continua funcionando normalmente no deployment local.

## Nivel 3: Servidor Local Indisponivel

Futuro Offline-First.

Preparar arquitetura para:

- local cache;
- operation queue;
- idempotency;
- sync;
- conflict resolution;
- versioning;
- auditoria local;
- replay seguro.

## Limite Atual

DOC-008 nao implementa Offline-First completo, SQLite local, fila local, sync real ou resolucao de conflitos.
