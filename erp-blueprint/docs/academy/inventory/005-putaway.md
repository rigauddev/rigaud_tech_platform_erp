# Put Away

Put Away é a etapa que transforma mercadoria recebida em estoque disponível.

## Antes Do Put Away

No Goods Receipt, a mercadoria já existe fisicamente, mas permanece pendente:

```text
putaway_pending_quantity > 0
available_quantity = 0
```

Isso evita vender ou consumir um item que ainda não foi guardado no local correto.

## Depois Do Put Away

Ao confirmar a armazenagem, o ERP reduz o saldo pendente e aumenta o saldo da localização final.

```text
InventoryMovement(type=putaway)
```

## Por Que Isso Importa

Esse padrão preserva rastreabilidade e prepara o ERP para:

- estoque por localização;
- auditoria;
- inventário;
- picking;
- restaurante;
- produção;
- IA futura baseada em eventos.
