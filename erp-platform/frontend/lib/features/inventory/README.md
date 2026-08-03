# Inventory

Feature Flutter do Inventory Engine.

Estrutura preparada em `data`, `domain` e `presentation`.

DOC-005 define o domínio antes da implementação da REST-003.

REST-003 adiciona:

- consulta de saldos;
- consulta de movimentações;
- formulário de ajuste;
- formulário de reserva;
- Riverpod controllers;
- repository/data source com Dio.

REST-009 adiciona:

- aba Put Away;
- confirmação por documento, produto, localização e quantidade;
- histórico de armazenagens filtrado por `business_process`;
- repository/data source para `POST /api/v1/inventory/putaway`.

As telas não implementam regra de negócio. Validações críticas permanecem no backend.
