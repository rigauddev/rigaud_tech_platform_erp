# Academy — Receiving Documents

Receiving Document é o registro administrativo da chegada de mercadorias.

Ele existe antes da entrada física no estoque.

## Por Que Separar

ERPs e WMS modernos separam documento, recebimento físico e endereçamento para preservar rastreabilidade.

Na REST-007 o ERP registra:

- documento;
- itens;
- quantidades pedidas, recebidas, avariadas e pendentes;
- status operacional.

Ele ainda não registra:

- `InventoryMovement`;
- atualização de `InventoryBalance`;
- put away.

## Regra De Ouro

Saldo nunca deve ser alterado diretamente.

Toda mudança futura de estoque deve nascer de `InventoryMovement`, e o `InventoryBalance` deve ser tratado como projeção auditável.

## Próxima Etapa

REST-008 implementará Goods Receipt, que confirma a entrada física e poderá gerar movimentos.
