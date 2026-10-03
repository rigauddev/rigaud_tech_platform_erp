# Inventory Validation

## Receiving Documents

REST-007 valida:

- filial ativa obrigatória;
- depósito existente, ativo e pertencente à filial ativa;
- número do documento único por tenant e filial enquanto não excluído;
- pelo menos um item;
- produto existente no tenant;
- quantidades não negativas;
- `received_quantity + damaged_quantity <= ordered_quantity`.

## Goods Receipt

REST-008 valida:

- filial ativa obrigatória;
- documento existente no tenant;
- documento pertencente à filial ativa;
- documento não pode estar `received`, `putaway_pending` ou `cancelled`;
- warehouse do documento deve existir, estar ativo e pertencer à filial ativa;
- ao menos um item deve possuir `received_quantity > 0`.

## Put Away

REST-009 valida:

- filial ativa obrigatória;
- documento existente no tenant;
- documento pertencente à filial ativa;
- documento deve estar em `putaway_pending`;
- produto deve existir entre os itens do documento;
- localização deve existir, estar ativa e pertencer ao mesmo tenant, filial e warehouse do documento;
- quantidade deve ser maior que zero;
- quantidade não pode exceder `putaway_pending_quantity`;
- ao zerar a pendência, o documento passa para `available`.

## Quantidade

- Deve ser maior que zero.
- Usa precisão decimal de 3 casas.
- Não aceita valores inválidos ou negativos.

## Ajuste De Saída

Não pode reduzir saldo abaixo da disponibilidade.

```text
available_quantity >= quantity
```

## Reserva

Não altera saldo físico.

Só pode ser criada se houver disponibilidade:

```text
physical_quantity - reserved_quantity >= quantity
```

## Liberação De Reserva

- reserva deve existir no tenant;
- reserva deve estar ativa;
- liberação gera novo movimento;
- reserva liberada não pode ser liberada novamente.

## Produto

O produto deve existir no tenant autenticado.

Produto de outro tenant deve ser tratado como inexistente.

## Filial

Operações de escrita exigem filial ativa resolvida pelo backend.
