# Partners And Resellers Knowledge

Arquitetura futura de documentacao para parceiros e revendedores.

## Publicos

- revendedores;
- parceiros de implantacao;
- parceiros comerciais;
- suporte tecnico;
- futuros operadores white-label.

## Conteudos Futuros

- onboarding do parceiro;
- gestao de clientes;
- planos;
- modulos;
- assinaturas;
- suporte;
- implantacao;
- troubleshooting;
- materiais comerciais;
- limites de acesso.

## Regra Arquitetural

Partner/Reseller nao e tenant.

Modelo:

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

## Fora Do Escopo

DOC-009 nao implementa portal, permissoes de parceiro, white-label, billing, comissoes ou suporte integrado.
