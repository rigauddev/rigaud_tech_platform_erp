# SaaS Foundation

DEV-011 cria a fundação comercial da plataforma.

Esta task não implementa cobrança real.

## Módulos

- `plan`
- `subscription`
- `entitlements`
- `feature_flags`
- `billing`

## Conceitos

`Plan` define o pacote contratado.

`Subscription` vincula uma empresa a um plano.

`Entitlements` dizem o que uma empresa pode usar.

`Feature Flags` ligam ou desligam recursos sem espalhar condicionais pelo ERP.

`Billing` registra eventos de cobrança e usa Strategy Pattern para provedores.

## Billing Provider

Implementado nesta task:

- `FakeBillingProvider`

Preparados para tasks futuras:

- Asaas
- Stripe
- Mercado Pago

## Status

Assinaturas suportam:

- `trial`
- `active`
- `past_due`
- `suspended`
- `cancelled`
- `expired`

`past_due` mantém a plataforma dentro do grace period.

Bloqueios reais de funcionalidades serão integrados em tasks futuras.

## Fora do Escopo

- cobrança real;
- webhooks externos reais;
- notas fiscais;
- marketplace;
- bloqueios comerciais nos módulos existentes.
