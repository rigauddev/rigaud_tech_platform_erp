# Academy — Inventory Engine Implementation

REST-003 transforma o domínio documentado na DOC-005 na primeira engine executável do ERP.

## Ideia Principal

Produto não possui saldo.

Saldo pertence ao Inventory Engine e é controlado por:

- empresa;
- filial;
- produto;
- warehouse futuro;
- location futura.

## Movimento Como Fonte De Verdade

O saldo projetado (`InventoryBalance`) é atualizado por operações que também registram movimentos.

Isso permite responder:

- quanto tenho agora;
- quanto está reservado;
- quanto está disponível;
- qual operação alterou o saldo;
- qual usuário originou a operação.

## Reserva Não Baixa Estoque Físico

Uma reserva apenas aumenta `reserved_quantity`.

Disponível:

```text
physical_quantity - reserved_quantity
```

Quando a venda ou pedido for implementado, uma task futura consumirá a reserva e criará o movimento de saída.

## Ajuste

Ajuste é a forma controlada de corrigir saldo.

REST-003 suporta:

- entrada por ajuste;
- saída por ajuste.

Toda saída valida disponibilidade para impedir saldo físico negativo.

## Por Que Isso Ajuda O Restaurante

Antes de mesa, QR Code e pedido, precisamos saber se existe saldo disponível.

Com REST-003, o MVP consegue começar a testar:

```text
Produto
    ↓
Categoria
    ↓
Saldo
    ↓
Reserva futura por pedido
```
