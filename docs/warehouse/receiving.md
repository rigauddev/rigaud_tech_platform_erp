# Warehouse Receiving

REST-007 inicia a EPIC-003 Inbound Logistics.

O Warehouse continua sendo a estrutura física:

```text
Company
  -> Branch
  -> Warehouse
  -> Zone
  -> Location
```

O Receiving Document registra a entrada documental da mercadoria no warehouse da filial ativa.

REST-008 adiciona a confirmação física por Goods Receipt.

REST-009 adiciona Put Away, confirmando a armazenagem em uma localização final.

## Fluxo Planejado

```text
Receiving Document
  -> Goods Receipt
  -> Put Away
  -> Inventory Balance
```

## Uso No Restaurante E Varejo

Restaurante:

- notas de compra de ingredientes;
- conferência de bebidas;
- separação posterior para câmara fria, bar e cozinha.

Varejo:

- chegada de coleção;
- conferência de peças;
- separação posterior para estoque, vitrine e reserva.
