# Inventory

Documentação do Inventory Engine.

A DOC-005 congela o domínio antes da implementação REST-003.

REST-003 implementa a primeira versão executável do Inventory Engine.

REST-007 adiciona documentos de recebimento, sem movimentar estoque.

REST-008 adiciona Goods Receipt, gerando movimento de recebimento e saldo físico pendente de put away.

REST-009 adiciona Put Away, movendo quantidade pendente para localização final e liberando disponibilidade por `InventoryMovement`.

REST-010 adiciona Inventory Transactions, expondo `InventoryMovement` como livro razao imutavel e filtravel.

REST-011 adiciona Inventory Count, com documentos de contagem fisica e divergencias registradas como movimentos `count` imutaveis.

Documentos principais:

- `api.md`;
- `endpoints.md`;
- `entities.md`;
- `events.md`;
- `permissions.md`;
- `putaway.md`;
- `transactions.md`;
- `counts.md`;
- `validation.md`.
