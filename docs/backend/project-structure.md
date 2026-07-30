# Backend Project Structure

Estrutura técnica do backend após a DEV-002.

```text
erp-platform/backend/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── database/
│   ├── db/
│   ├── exceptions/
│   ├── middlewares/
│   ├── modules/
│   ├── security/
│   ├── shared/
│   └── utils/
├── migrations/
│   └── versions/
├── requirements/
└── tests/
```

## Database

`app/database` concentra a fundação técnica de persistência:

- base declarativa.
- convenção de nomes.
- engine e sessão assíncronas.
- mixins técnicos.
- tipos compartilhados.
- contexto de tenant.

Detalhes em `docs/backend/database-core.md`.

## Módulos

Cada módulo em `app/modules` possui a mesma estrutura:

```text
module/
├── application/
├── domain/
├── infrastructure/
├── presentation/
├── tests/
└── README.md
```

Módulos preparados:

- `auth`
- `companies`
- `users`
- `products`
- `restaurant`
- `fashion`
- `inventory`
- `sales`
- `finance`
- `delivery`
- `fiscal`

## Camadas

- `domain`: contratos e conceitos centrais futuros do módulo.
- `application`: use cases e orquestração futura.
- `infrastructure`: adaptadores externos e persistência futura.
- `presentation`: rotas e schemas HTTP futuros.
- `tests`: testes isolados por módulo.

Nenhuma regra de negócio foi implementada nesta estrutura.
