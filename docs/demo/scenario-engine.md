# Scenario Engine

O Scenario Engine é o blueprint dos cenários operacionais de demonstração.

Na DOC-003 ele permanece documental porque os módulos de mesas, setores, estoque, clientes, pedidos, delivery, caixa e vendas ainda não existem na base atual.

## Cenário Restaurante Futuro

Quando os módulos necessários existirem, o seed deverá preparar:

- Mesa 1 com pedido aberto;
- Mesa 5 com pedido originado por QR Code;
- Mesa 12 aguardando pagamento;
- Mesa 20 com pedido delivery;
- cozinha com preparo em andamento;
- garçons vinculados às mesas;
- produtos com estoque mínimo, saldo disponível e itens em falta.

## Cenário Loja Futuro

Quando os módulos necessários existirem, o seed deverá preparar:

- venda em andamento;
- pré-venda;
- produto reservado;
- produto em falta;
- produto em promoção;
- clientes recorrentes.

## Evolução Por Módulo

O seed deve continuar separado por módulo:

- Base;
- SaaS;
- Restaurant;
- Retail;
- CRM;
- Finance;
- Reports.

Novos comandos devem ser adicionados somente quando as tabelas e use cases correspondentes existirem.

