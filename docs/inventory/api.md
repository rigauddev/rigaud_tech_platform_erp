# Inventory API

REST-003 implementa a primeira versão executável do Inventory Engine.

## Princípio

Saldo não é alterado diretamente por endpoint.

Toda alteração nasce de uma operação rastreável:

- ajuste de estoque;
- reserva de estoque;
- liberação de reserva.

Cada operação gera:

- atualização da projeção `InventoryBalance`;
- registro imutável em `InventoryMovement`;
- evento interno planejado;
- auditoria persistida.

## Escopo REST-003

Implementado:

- consulta de saldos;
- consulta de movimentações;
- ajuste de entrada e saída;
- reserva de saldo disponível;
- liberação de reserva.

Fora do escopo:

- CRUD de warehouses;
- CRUD de stock locations;
- inventário físico;
- transferências;
- consumo de reserva por venda;
- Kafka real.

## Contrato

Todos os endpoints usam o envelope padrão:

```json
{
  "success": true,
  "code": "INVENTORY_ADJUSTMENT_CREATED",
  "message": "Ajuste de estoque registrado com sucesso.",
  "data": {},
  "request_id": "request-id",
  "correlation_id": "correlation-id",
  "timestamp": "2026-08-01T00:00:00Z"
}
```

## Multi-Tenant E Multi-Filial

- `tenant_id` é sempre resolvido pelo usuário autenticado.
- `branch_id` usa a filial ativa do usuário.
- O frontend não envia `tenant_id`.
- Operações de estoque exigem filial ativa.
- Consultas são filtradas por tenant e filial ativa por padrão.

## Referências Oficiais

- FastAPI `APIRouter` para modularização de rotas.
- SQLAlchemy 2.x async com `AsyncSession`.
- Alembic com integração async via `run_sync`.
