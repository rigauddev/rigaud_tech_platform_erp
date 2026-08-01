# Inventory Permissions

REST-003 prepara o Inventory Engine para RBAC, mas não cria um módulo completo de permissões.

## Regras Atuais

- usuário autenticado obrigatório;
- tenant resolvido pelo backend;
- filial ativa obrigatória para operações de escrita;
- consultas usam tenant e filial ativa por padrão;
- auditoria registra ator em operações críticas.

## Perfis Planejados

Perfis que devem consumir o módulo em fases futuras:

- administrador;
- gerente;
- estoque;
- caixa;
- garçom;
- cozinha;
- vendedor.

## Operações Sensíveis

Exigem auditoria:

- ajuste de entrada;
- ajuste de saída;
- reserva;
- liberação de reserva.

## Evolução

Uma task futura deve conectar permissões explícitas ao RBAC:

- `inventory.balance.read`;
- `inventory.movement.read`;
- `inventory.adjustment.create`;
- `inventory.reservation.create`;
- `inventory.reservation.release`.
