# Hybrid Deployment

Hybrid combina servidor local e Rigaud Cloud.

## Arquitetura Planejada

```text
Local Server
      ↓
Sync Gateway
      ↓
Rigaud Cloud
```

## Decisao

Nem todos os dados precisam ser enviados para a nuvem.

Cada modulo devera declarar futuramente:

- dados sincronizados;
- dados locais;
- eventos sincronizados;
- telemetria;
- backups;
- retencao;
- dados sensiveis ou regulados.

## Sync Gateway

O Sync Gateway e futuro. Ele devera tratar:

- fila de eventos;
- idempotencia;
- retry;
- versionamento de schema;
- resolucao de conflitos;
- observabilidade;
- auditoria.

## Limite Atual

DOC-008 nao implementa sincronizacao, filas, consumers, cloud real ou portal de operacao.
