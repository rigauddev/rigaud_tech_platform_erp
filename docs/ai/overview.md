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

## Limite Atual

Não há providers, agentes, prompts, RAG, embeddings, memória, ferramentas MCP ou chamadas externas nesta task.
