# Inventory Permissions

REST-003 prepara o Inventory Engine para RBAC, mas não cria um módulo completo de permissões.

REST-007 usa o usuário autenticado, tenant e filial ativa para operar documentos de recebimento.

Permissões planejadas:

- listar recebimentos;
- criar recebimento;
- editar recebimento;
- alterar status;
- cancelar recebimento.

REST-008 adiciona permissão planejada:

- confirmar recebimento físico.

REST-009 adiciona permissão planejada:

- confirmar put away.

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
- `inventory.putaway.confirm`.
