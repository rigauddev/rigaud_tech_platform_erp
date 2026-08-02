# Warehouse API

Base path:

```text
/api/v1/warehouses
```

## Endpoints

```text
GET    /warehouses
GET    /warehouses/{id}
POST   /warehouses
PUT    /warehouses/{id}
POST   /warehouses/{id}/default
DELETE /warehouses/{id}
```

## Payload De Criação

```json
{
  "code": "MAIN",
  "name": "Depósito Principal",
  "description": "Estoque principal da filial",
  "address": "Fundos da loja",
  "is_default": true,
  "is_active": true
}
```

## Regras

- O backend resolve `tenant_id` e `branch_id`.
- Código é único por tenant e filial.
- Apenas um depósito pode ser padrão por filial.
- Depósito padrão precisa estar ativo.
- Remoção é soft delete.
- Operações críticas geram auditoria.

## Eventos

- `warehouse.created`;
- `warehouse.updated`;
- `warehouse.default.changed`;
- `warehouse.deleted`.
