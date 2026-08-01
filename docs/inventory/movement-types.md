# Tipos De Movimentação

Tipos congelados para REST-003:

- `INITIAL`;
- `PURCHASE`;
- `SALE`;
- `RETURN`;
- `LOSS`;
- `TRANSFER`;
- `PRODUCTION`;
- `CONSUMPTION`;
- `ADJUSTMENT`;
- `COUNT`.

## Direção Do Saldo

Entradas:

- `INITIAL`;
- `PURCHASE`;
- `RETURN`;
- `PRODUCTION`;
- `COUNT`, quando divergência positiva.

Saídas:

- `SALE`;
- `LOSS`;
- `CONSUMPTION`;
- `COUNT`, quando divergência negativa.

Neutras ou compostas:

- `TRANSFER`;
- `ADJUSTMENT`.

## Regras Gerais

- todo movimento precisa de origem técnica ou motivo;
- movimentos confirmados não devem ser alterados;
- estorno deve gerar movimento oposto;
- transferência deve gerar saída na origem e entrada no destino;
- contagem deve gerar ajustes derivados, não editar saldo diretamente.

