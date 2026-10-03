# Receiving Flutter

REST-007 adiciona a feature:

```text
erp-platform/frontend/lib/features/receiving_documents
```

## Camadas

- `domain`: entidades, inputs, repository interface e use cases;
- `data`: Dio data source e implementação do repository;
- `presentation`: controller Riverpod, lista, formulário e detalhe.

## Rotas

- `/receiving-documents`
- `/receiving-documents/new`
- `/receiving-documents/:documentId`
- `/receiving-documents/:documentId/edit`

## Telas

- lista com filtros por depósito, status e pesquisa;
- cadastro com documento e itens;
- edição;
- detalhe;
- mudança de status.

O frontend não calcula saldo e não dispara recebimento físico. Ele apenas opera o documento documental da REST-007.
