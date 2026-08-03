# Warehouse Management

REST-004 implementa o cadastro de depósitos do Inventory Engine.

Warehouse é a unidade lógica de armazenagem dentro de uma filial.

Exemplos:

- Depósito Principal;
- Câmara Fria;
- Bar;
- Cozinha;
- Estoque;
- Vitrine;
- Reserva;
- Expedição.

## Escopo

Implementado:

- CRUD de depósitos;
- depósito padrão por filial;
- ativação e desativação;
- soft delete;
- auditoria;
- API com envelope padrão;
- telas Flutter para lista, cadastro, edição e detalhe;
- dados demo para restaurante e varejo.

Fora do escopo:

- Stock Locations;
- Goods Receipt;
- transferências;
- QR Code físico do depósito;
- leitura por código de barras.

## Relação Com Inventory

`warehouse_id` passa a referenciar `warehouses.id` em:

- `inventory_balances`;
- `inventory_movements`;
- `inventory_adjustments`;
- `inventory_reservations`.

Operações de estoque que informarem `warehouse_id` validam tenant, filial e status ativo do depósito.

REST-005 adiciona `WarehouseZone` como camada entre depósito e localizações físicas. A documentação está em `docs/warehouse/zones.md`.

REST-006 adiciona `WarehouseLocation` como endereço físico ou bin dentro das zonas. A documentação está em `docs/warehouse/locations.md`.

REST-007 adiciona documentos de recebimento ligados ao warehouse da filial ativa. A documentação está em `docs/warehouse/receiving.md`.

REST-008 adiciona Goods Receipt e mantém quantidade recebida pendente de put away. A documentação está em `docs/warehouse/goods-receipt.md`.

## Demo Environment

`make demo`, `make demo-restaurant`, `make demo-retail` e `make playground` criam depósitos, zonas, localizações e documentos de recebimento demo por filial.

Restaurante:

- Matriz: Depósito Principal, Câmara Fria, Bar e Cozinha;
- Delivery: Expedição Delivery;
- Food Truck: Estoque Food Truck.

Varejo:

- Shopping: Estoque, Vitrine e Reserva;
- Centro: Estoque Centro.
