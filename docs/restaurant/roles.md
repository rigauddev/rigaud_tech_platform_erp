# Papéis Operacionais do Restaurante

Papéis de Restaurant Operations são perfis funcionais sobre o RBAC existente. Permissões efetivas continuam resolvidas pelo backend com tenant, filial ativa, role e permissões; a tela não confia em um papel informado pelo cliente.

| Papel | Responsabilidade futura | Limites |
| --- | --- | --- |
| Gestor da operação | configurar ambiente, acompanhar operação e exceções | não substitui permissões de plataforma |
| Atendente/Garçom | atender mesas e lançar pedidos | somente setores/mesas autorizados |
| Responsável da mesa | acompanhar a mesa e receber notificações | pode ser diferente de quem lançou o pedido |
| Cozinha/Bar | produzir e atualizar itens em estação | não fecha conta nem altera preço |
| Caixa/PDV | abrir/fechar sessão e concluir pagamento | não administra cadastros globais |
| Cliente | consultar menu e realizar pedido no canal autorizado | acesso limitado ao contexto de mesa/canal |

## Rastreabilidade do pedido

Todo pedido futuro separará:

- `order_entered_by`: usuário que registrou o pedido;
- `table_responsible_waiter`: garçom responsável pela mesa no momento operacional;
- ator de alteração, envio, cancelamento e fechamento;
- tenant, filial, canal e Request ID.

Essa separação permite troca de garçom, pedido pelo QR e auditoria sem atribuir uma ação ao usuário errado.
