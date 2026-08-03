# Academy — Goods Receipt

Goods Receipt é a confirmação física da chegada da mercadoria.

Na REST-007 o ERP registrava apenas o documento. Na REST-008 o ERP passa a registrar o efeito físico do recebimento.

## Por Que Não Liberar Imediatamente

Em WMS modernos, receber não significa disponibilizar.

O produto pode estar:

- descarregado;
- conferido;
- aguardando inspeção;
- aguardando endereçamento;
- pendente de armazenagem.

Por isso a REST-008 cria saldo físico, mas marca a quantidade como pendente de put away.

## Movimento Primeiro

Toda alteração de saldo nasce de `InventoryMovement`.

O `InventoryBalance` é uma projeção atualizada a partir da movimentação confirmada.

## Resultado

Depois da REST-008:

```text
physical_quantity > 0
putaway_pending_quantity > 0
available_quantity = 0
```

Depois da REST-009, o Put Away poderá liberar a quantidade disponível.
