# Inventory Transactions

## Conceito

Inventory Transactions sao o historico auditavel das mudancas de estoque.

No Rigaud Tech Platform ERP, a transacao nasce de `InventoryMovement`.

## Por Que Nao Editar Saldo Direto

Saldo atual e fotografia.

Transacao e historia.

Se o saldo fosse alterado diretamente, perderiamos:

- origem;
- motivo;
- ator;
- processo;
- auditoria;
- capacidade de reconstruir o estoque.

## Fluxo

```text
Operacao
  -> InventoryMovement
  -> InventoryBalance
  -> Auditoria
  -> Eventos futuros
```

## Exemplos

- Goods Receipt cria transacao `receipt`.
- Put Away cria transacao `putaway`.
- Ajuste cria transacao `adjustment_in` ou `adjustment_out`.
- Reserva cria transacao `reservation_created`.
- Liberacao cria transacao `reservation_released`.

## Futuro

Restaurante, vendas, caixa, producao, perdas, inventario e transferencias tambem deverao registrar transacoes.

Isso prepara relatórios, auditoria, IA e conciliacao offline sem remodelar o Inventory Engine.
