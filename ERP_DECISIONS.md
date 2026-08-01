# ERP Decisions

Decisões de produto, domínio e arquitetura que não devem ser rediscutidas sem ADR ou task específica.

## Produto E Plataforma

- O nome oficial é `Rigaud Tech Platform ERP`.
- A plataforma é modular, multi-tenant e multiplataforma.
- O Core deve ser reutilizado por Restaurante, Loja e futuros segmentos.
- Engines compartilhadas devem atender múltiplos segmentos.

## Tenant E Filial

- `Company` é a raiz oficial do tenant.
- `tenant_id = companies.id`.
- `Branch` representa filial operacional dentro de um tenant.
- O frontend nunca define `tenant_id` confiável.
- O backend resolve tenant e filial pelo usuário autenticado e contexto ativo.

## Produtos E Estoque

- Produto não possui saldo.
- Saldo pertence ao Inventory Engine.
- Estoque é controlado por tenant, filial, warehouse e location quando aplicável.
- Reserva não altera saldo físico.
- Movimento confirmado não é editado.
- Correção de estoque deve gerar novo movimento ou ajuste.

## Segurança E Acesso

- Login usa tenant, email e senha.
- JWT é curto e controlado pelo backend.
- Refresh token é opaco, rotacionável e persistido apenas como hash.
- MFA pode ser habilitado ou desabilitado por usuário.
- Canais MFA preparados: email, telefone e aplicativo TOTP.
- Superusuários administrativos devem ser validados explicitamente.

## API, Auditoria E Observabilidade

- Toda API usa envelope padronizado.
- Mensagens e códigos ficam no catálogo central.
- Eventos críticos devem ser auditados.
- `request_id` acompanha resposta e logs.
- Dados sensíveis não devem aparecer em logs.

## SaaS E Feature Flags

- SaaS fica desacoplado dos módulos comerciais.
- Planos, assinaturas, entitlements e billing não devem vazar para regra de negócio segmentada.
- Bloqueios comerciais passam por entitlements e feature flags.
- Billing real entra por Strategy Pattern em task específica.

## Demo Environment

- Tudo que for desenvolvido deve ser demonstrável.
- Módulos funcionais devem incluir dados demo ou registrar por que ainda não podem ser demonstrados.
- Cenários completos só devem materializar tabelas existentes.

## Offline Futuro

- Offline-first é planejado.
- SQLite local só entra em task futura.
- Operações offline devem considerar idempotência, fila, retry, conflitos e auditoria.

