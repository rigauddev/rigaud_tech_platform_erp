# Academy — Warehouse Management

Warehouse é o depósito lógico de uma filial.

Ele responde:

- onde o estoque está armazenado em alto nível;
- qual depósito é o padrão da filial;
- quais depósitos estão ativos;
- qual depósito será usado por saldos, reservas e movimentações.

## Warehouse Não É Location

Warehouse é o agrupador.

Stock Location será o endereço físico interno.

Exemplo:

```text
Depósito Principal
    ↓
Corredor A
    ↓
Prateleira 01
    ↓
Nível 02
```

REST-004 implementa o primeiro nível.

REST-005 implementará os endereços internos.

## Por Que Isso Importa

Restaurante:

- Câmara Fria;
- Bar;
- Cozinha;
- Salão.

Loja:

- Estoque;
- Vitrine;
- Reserva;
- Expedição.

Com isso, o ERP começa a formar um fluxo real de armazenagem antes de pedidos e vendas.
