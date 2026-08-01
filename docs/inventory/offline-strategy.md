# Offline Strategy

DOC-005 não implementa offline.

Ela congela as perguntas e restrições que REST-003 deve respeitar para permitir offline-first em tarefa futura.

## Pode Funcionar Offline?

Parcialmente.

Operações que podem ser preparadas offline:

- contagem física;
- ajuste pendente;
- reserva local pendente;
- transferência pendente;
- venda local em modo contingência.

Operações que exigem sincronização antes de confirmação final:

- consumo definitivo de estoque compartilhado;
- transferência entre filiais;
- baixa que possa gerar saldo negativo;
- reserva que depende de disponibilidade global.

## Sincronização Futura

Toda operação offline deve possuir:

- `client_operation_id`;
- `idempotency_key`;
- `tenant_id`;
- `branch_id`;
- data local;
- data recebida pelo servidor;
- origem do dispositivo;
- usuário responsável.

## Conflitos

Conflitos previstos:

- saldo insuficiente após sincronização;
- mesma reserva consumida por outra operação;
- produto inativo localmente ativo no cache;
- transferência recebida com divergência;
- contagem baseada em snapshot vencido.

## Resolução

Estratégias planejadas:

- bloquear confirmação e exigir revisão;
- gerar ajuste pendente;
- priorizar servidor para dados mestres;
- preservar operação local como pendência auditável;
- permitir retry idempotente.

## Fila E Retry

O cliente futuro deve manter fila local com:

- status `pending`;
- status `syncing`;
- status `synced`;
- status `failed`;
- contador de tentativas;
- última mensagem de erro;
- próxima tentativa.

