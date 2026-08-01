# Integrações

## Products

Inventory depende de Product para identificar itens controláveis.

Regras:

- produto inativo não deve receber novas entradas operacionais, salvo ajuste técnico;
- produto removido por soft delete preserva histórico;
- tipo de produto pode definir se estoque é obrigatório.

## Orders

Order Engine deverá usar reservas.

Fluxo planejado:

1. pedido criado;
2. Inventory reserva produtos;
3. pedido cancelado libera reserva;
4. pedido fechado consome reserva e gera saída.

## POS E Sales

POS Engine consome estoque no fechamento da venda.

Regras:

- venda concluída gera `SALE`;
- devolução gera `RETURN`;
- cancelamento tenta estornar se a operação já tiver movimentado estoque.

## Financial

Financial Engine não altera estoque diretamente.

Ele consome eventos para:

- custo médio futuro;
- CMV;
- conciliação;
- relatórios.

## Restaurant

Restaurant Engine usa Inventory para:

- ingredientes;
- produtos preparados;
- consumo por pedido;
- baixa por produção;
- perdas.

## Retail

Retail usa Inventory para:

- loja;
- depósito;
- expositor;
- reserva;
- transferência entre filiais.

## Reports

Reporting Engine consome transações e eventos para:

- posição de estoque;
- estoque mínimo;
- ruptura;
- giro;
- divergências;
- histórico de movimentações.

