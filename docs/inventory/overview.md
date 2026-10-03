# Inventory Engine Domain

DOC-005 congela oficialmente o domínio do Inventory Engine antes da implementação da REST-003.

O Inventory Engine é um módulo compartilhado do Rigaud Core. Ele deve atender Restaurante, Loja, Delivery, Financeiro, Relatórios e futuros canais sem acoplamento a um segmento específico.

## Objetivo

O Inventory Engine controla disponibilidade física e lógica de produtos por empresa, filial e local de estoque.

Ele deve responder:

- quanto existe;
- onde está;
- quanto está reservado;
- quanto está disponível;
- por que o saldo mudou;
- qual evento operacional originou cada mudança.

## Escopo Da REST-003

A implementação futura deve nascer como engine reutilizável, não como estoque exclusivo de restaurante.

REST-003 implementará a primeira versão do Inventory Engine consumida pelo MVP Restaurante.

## Fora Do Escopo Da DOC-005

Esta task não cria:

- tabelas;
- migrations;
- endpoints;
- telas;
- regras executáveis;
- integrações reais com Kafka;
- sincronização offline.

Ela congela contrato de domínio, eventos, estados, fluxos e limites arquiteturais.

## Entidades

- `Warehouse`;
- `StockLocation`;
- `InventoryBalance`;
- `InventoryMovement`;
- `InventoryReservation`;
- `InventoryAdjustment`;
- `InventoryCount`;
- `InventoryTransfer`;
- `InventoryTransaction`.

## Princípios

- Toda entidade operacional do estoque é multi-tenant.
- Toda entidade operacional deve possuir `tenant_id`.
- Toda operação dependente de filial deve possuir `branch_id`.
- Saldo disponível nunca deve ser inferido pelo frontend.
- Movimentações devem ser auditáveis e rastreáveis.
- Ajustes manuais devem registrar motivo.
- Reservas não devem alterar saldo físico.
- Transferências devem preservar origem, destino e trilha de auditoria.
- Eventos internos devem ser publicados por contrato estável.
- Kafka é planejado, mas não é dependência da primeira implementação.

