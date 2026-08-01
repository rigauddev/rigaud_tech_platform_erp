# Academy — Inventory Engine Domain

O Inventory Engine é o domínio compartilhado de estoque do Rigaud Tech Platform ERP.

Ele não pertence apenas ao Restaurante. Ele será usado por Restaurante, Loja, Delivery, POS, Financeiro e Relatórios.

## Ideia Central

Estoque não é apenas uma quantidade.

Estoque é a combinação de:

- produto;
- empresa;
- filial;
- warehouse;
- location;
- saldo físico;
- saldo reservado;
- saldo disponível;
- movimentos;
- transações;
- eventos.

## Por Que Engine?

Uma engine nasce para ser reutilizada.

Se o Restaurante baixa ingrediente e a Loja reserva produto, ambos devem usar os mesmos conceitos centrais:

- saldo;
- movimento;
- reserva;
- ajuste;
- inventário;
- transferência.

## Regra De Ouro

Movimentos confirmados não são editados.

Quando algo precisa ser corrigido, o sistema gera um novo movimento ou ajuste. Isso preserva auditoria e torna o saldo explicável.

## Offline

O offline deve ser planejado desde o domínio.

Operações offline precisam de idempotência, fila local, resolução de conflitos e trilha auditável.

DOC-005 não implementa offline, mas impede que REST-003 nasça incompatível com ele.

## Eventos

Eventos como `inventory.reserved`, `inventory.adjusted` e `inventory.out.of.stock` permitem que outros módulos reajam sem acoplamento direto.

No futuro, esses eventos poderão sair por Kafka sem alterar o domínio.

