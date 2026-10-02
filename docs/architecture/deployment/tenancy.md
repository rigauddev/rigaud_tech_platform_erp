# Tenant And Deployment

## Tenant

Tenant e a empresa cliente.

No banco:

```text
tenant_id = companies.id
```

## Login

Usuario comum nao escolhe empresa no login.

O backend resolve:

- user;
- tenant/company;
- branch;
- role;
- permissions;
- access scope.

## Deployment

Deployment e a instalacao tecnica.

Tipos oficiais:

- `CLOUD_SHARED`;
- `CLOUD_DEDICATED`;
- `ON_PREMISE`;
- `HYBRID`.

## Migracao

Um tenant podera futuramente migrar:

```text
CLOUD -> ON_PREMISE
ON_PREMISE -> CLOUD
ON_PREMISE -> HYBRID
CLOUD_SHARED -> CLOUD_DEDICATED
```

Sem criar uma nova empresa.

O `tenant_id` deve permanecer estavel durante a migracao sempre que tecnicamente possivel.

## Regra De Ouro

Nunca usar deployment como substituto de tenant.
