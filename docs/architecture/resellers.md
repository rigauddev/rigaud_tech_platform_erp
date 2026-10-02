# Resellers And Partners

DOC-008 congela que reseller/partner nao e tenant.

## Modelo

```text
Rigaud Tech
  ↓
Partner/Reseller
  ↓
Customer
  ↓
Company/Tenant
  ↓
Branches
  ↓
Users
```

## Decisao

O tenant continua sendo a empresa cliente (`Company`).

Partner/Reseller e uma camada comercial e operacional futura, podendo administrar carteira, suporte, implantacoes e relacionamento, mas sem substituir o tenant.

## Fora Do Escopo

DOC-008 nao implementa:

- portal de reseller;
- tabela de partner;
- comissionamento;
- permissoes de suporte externo;
- white label.
