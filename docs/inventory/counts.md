# Inventory Count

REST-011 implementa a contagem fisica como um documento operacional auditavel. Ela compara uma fotografia do saldo esperado com a quantidade observada, sem editar `InventoryBalance` durante a contagem.

## Ciclo de vida

`draft` -> `in_progress` -> `finished` ou `cancelled`.

Ao concluir, cada divergencia gera um `InventoryMovement` imutavel do tipo `count`, com `origin_module=INVENTORY` e `business_process=COUNT`. O saldo projetado e atualizado no mesmo commit. Contagens canceladas nao geram movimentos nem alteram saldo.

## Endpoints

- `GET /api/v1/inventory/counts`
- `POST /api/v1/inventory/counts`
- `POST /api/v1/inventory/counts/{count_id}/start`
- `PUT /api/v1/inventory/counts/{count_id}/items/{item_id}`
- `POST /api/v1/inventory/counts/{count_id}/finish`
- `POST /api/v1/inventory/counts/{count_id}/cancel`

Todos exigem JWT, respeitam `tenant_id` e a filial ativa, usam o envelope padrao e registram auditoria.

## Limites desta task

Nao ha ajuste manual avancado, transferencia, leitura por coletor, lote/validade, bloqueio de localizacao ou contagem cega. Esses itens seguem para as tasks posteriores de estoque.
