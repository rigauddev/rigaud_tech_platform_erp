# Tipos De Movimentação

Tipos implementados até REST-009:

- `receipt`;
- `putaway`;
- `adjustment_in`;
- `adjustment_out`;
- `reservation_created`;
- `reservation_released`.

Tipos planejados:

- `sale`;
- `transfer`;
- `return`;
- `loss`;
- `consumption`;
- `count`.

## Direção Do Saldo

Entradas:

- `receipt`;
- `adjustment_in`;
- `return`;
- `count`, quando divergência positiva.

Saídas:

- `sale`;
- `loss`;
- `consumption`;
- `adjustment_out`;
- `count`, quando divergência negativa.

Neutras ou compostas:

- `putaway`;
- `transfer`;
- `reservation_created`;
- `reservation_released`.

## Rastreabilidade

A partir da REST-009, todo `InventoryMovement` registra:

- `origin_module`;
- `business_process`.

Esses campos permitem separar compra, put away, produção futura, venda, delivery, transferência, perda e inventário sem criar acoplamento entre módulos.

## Regras Gerais

- todo movimento precisa de origem técnica ou motivo;
- movimentos confirmados não devem ser alterados;
- estorno deve gerar movimento oposto;
- transferência deve gerar saída na origem e entrada no destino;
- contagem deve gerar ajustes derivados, não editar saldo diretamente.
