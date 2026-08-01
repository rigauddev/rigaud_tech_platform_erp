# Auditoria E Segurança

## Auditoria

Eventos críticos devem ser auditados:

- criação e alteração de warehouses;
- criação e alteração de locations;
- ajuste de saldo;
- transferência;
- reserva;
- liberação de reserva;
- finalização de inventário;
- detecção de estoque mínimo;
- detecção de ruptura.

## Logs

Logs técnicos devem conter:

- `request_id`;
- `correlation_id`;
- `tenant_id`;
- `branch_id`;
- `operation`;
- `source_module`;
- `source_id`.

Não registrar:

- tokens;
- senhas;
- dados sensíveis de usuários;
- payloads extensos sem sanitização.

## Segurança

Regras futuras:

- operações administrativas exigem membership ativo;
- ajustes podem exigir role específica;
- transferência entre filiais exige acesso à origem e ao destino;
- consultas sempre filtram por tenant;
- frontend nunca informa `tenant_id` confiável.

