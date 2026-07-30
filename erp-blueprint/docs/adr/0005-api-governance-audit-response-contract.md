# ADR 0005: Governança de API, Observabilidade e Auditoria

## Status

Aceita.

## Contexto

Os módulos Auth, Companies e Users já possuem fluxos críticos. Antes de iniciar módulos comerciais, a plataforma precisa de rastreabilidade, mensagens seguras, respostas consistentes e auditoria separada de logs técnicos.

## Decisão

Adotar:

- `request_id` gerado por requisição.
- `X-Correlation-ID` opcional, validado e limitado.
- Logs técnicos estruturados.
- Sanitização central de dados sensíveis.
- Catálogo central de códigos e mensagens.
- Envelope padrão para sucesso e erro.
- Auditoria persistida em `audit_events`.
- Consulta de auditoria somente para superusuários.
- Gestão de Tasks via Docs-as-Code.

## Consequências

- Módulos futuros devem declarar códigos, eventos de auditoria e logs técnicos.
- Mensagens internas não devem chegar ao cliente.
- Eventos críticos devem ser auditados na transação quando apropriado.
- Flutter passa a interpretar `code`, `message`, `errors` e `request_id`.
