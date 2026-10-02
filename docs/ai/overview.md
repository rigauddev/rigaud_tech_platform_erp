# AI Foundation

O projeto reserva a estrutura `erp-platform/backend/app/ai/` para IA, agentes e MCPs futuros.

Nenhuma funcionalidade de IA é implementada nesta etapa.

## Estrutura

```text
ai/
  providers/
  agents/
  prompts/
  tools/
  mcp/
  memory/
  embeddings/
  rag/
  events/
  README.md
```

## Diretriz

IA deve ser desacoplada do ERP por eventos.

Exemplo futuro:

```text
InventoryMovementCreated
  -> Kafka
  -> AI Event
  -> MCP Inventory
  -> Insight
```

Eventos de estoque como `inventory.receipt.confirmed` e `inventory.putaway.confirmed` já carregam origem funcional planejada por `origin_module` e processo operacional por `business_process`.

## AI Gateway E MCP Futuro

Arquitetura planejada:

```text
AI Gateway
  ↓
MCP
  ↓
Domain-specific tools
```

MCPs futuros:

- Finance;
- Inventory;
- Restaurant;
- Production;
- HR;
- Commercial.

Cada MCP devera respeitar tenant, branch, role, permissions e audit.

## Limite Atual

Não há providers, agentes, prompts, RAG, embeddings, memória, ferramentas MCP ou chamadas externas nesta task.
