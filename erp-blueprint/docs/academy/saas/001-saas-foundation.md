# SaaS Foundation

SaaS significa vender o ERP como serviço.

Na Rigaud Tech Platform ERP, a empresa continua sendo o tenant.

DEV-011 adiciona uma camada comercial acima do tenant:

- plano;
- assinatura;
- entitlements;
- feature flags;
- billing status.

## Entitlements

Entitlements evitam condicionais espalhadas pelo sistema.

Em vez de cada módulo decidir sozinho, a plataforma consulta se a empresa pode usar uma capacidade.

## Feature Flags

Feature flags permitem ativar recursos específicos por tenant ou globalmente.

## Billing Provider

O billing usa Strategy Pattern.

Nesta task existe apenas `FakeBillingProvider`.

Provedores reais ficam para tasks futuras.

## Grace Period

`past_due` representa atraso.

Durante o grace period, o sistema ainda pode funcionar.

Após isso, a assinatura pode ir para `suspended`.
