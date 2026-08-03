# Warehouse Goods Receipt

REST-008 confirma fisicamente mercadorias em um warehouse, mas ainda não as endereça para uma localização final.

## Relação Com Warehouse

O recebimento físico ocorre no `warehouse_id` do documento.

Até a REST-009:

- `location_id` permanece nulo no movimento de recebimento;
- quantidade fica pendente de put away;
- disponibilidade não é liberada.

## Fluxo WMS

```text
Receiving Document
  -> Goods Receipt
  -> Put Away Pending
  -> Put Away
  -> Available Stock
```

## Decisão

O Rigaud Tech Platform ERP adota separação entre receber e armazenar.

Isso permite que restaurante e varejo controlem mercadorias em conferência antes de liberar consumo, venda ou separação.
