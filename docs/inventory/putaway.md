# Put Away

REST-009 implementa a confirmação de armazenagem física após o Goods Receipt.

O fluxo oficial fica:

```text
Receiving Document
  -> Goods Receipt
  -> Put Away
  -> Available Stock
```

## Decisão Arquitetural

Put Away não cria nova entidade operacional nesta task. Ele é um serviço de aplicação que confirma a movimentação da mercadoria recebida para uma `WarehouseLocation`.

A alteração de saldo continua acontecendo somente acompanhada por `InventoryMovement`.

## Endpoint

```http
POST /api/v1/inventory/putaway
```

Payload:

```json
{
  "document_id": "uuid",
  "product_id": "uuid",
  "location_id": "uuid",
  "quantity": "10.000",
  "reason": "Enderecamento para prateleira A"
}
```

Resposta:

- documento atualizado;
- saldo de origem;
- saldo de destino;
- movimento `putaway`.

## Regras

- O documento deve estar em `putaway_pending`.
- A localização deve pertencer ao mesmo tenant, filial e warehouse do documento.
- A localização deve estar ativa.
- A quantidade deve ser positiva.
- A quantidade não pode exceder a quantidade recebida do item.
- A quantidade não pode exceder `putaway_pending_quantity`.
- Ao zerar `putaway_pending_quantity`, o documento passa para `available`.

## Projeção De Saldo

Durante o Goods Receipt:

```text
warehouse/location=null:
physical += received
putaway_pending += received
available = 0
```

Durante o Put Away:

```text
warehouse/location=null:
physical -= quantity
putaway_pending -= quantity

warehouse/location=target:
physical += quantity
available += quantity
```

O movimento registra:

```text
movement_type = putaway
origin_module = PURCHASE
business_process = PUTAWAY
event_name = inventory.putaway.confirmed
```

## Rastreabilidade

REST-009 adiciona os campos:

- `origin_module`;
- `business_process`.

Esses campos permitem analisar estoque por origem e processo sem acoplar os módulos comerciais ao Inventory Engine.

## Impacto Para Restaurant Production

Produção de restaurante não será implementada agora.

A decisão congelada é que pratos não baixam estoque diretamente na venda. O fluxo futuro será:

```text
Recipe Engine
  -> Production Planning
  -> Daily Production
  -> Consumption
  -> Waste
  -> Forecast
  -> AI Insights
```

Quando essa EPIC for implementada, o consumo de insumos usará `InventoryMovement` com:

```text
origin_module = RESTAURANT_PRODUCTION
business_process = PRODUCTION
```

## Preparação Para IA/MCP

O evento interno `inventory.putaway.confirmed` fica preparado para um futuro Event Bus/Kafka.

Nenhum consumer de IA foi implementado nesta task.

## Validação Multiplataforma

REST-009 foi validada com:

- `flutter analyze`;
- `flutter test`;
- `flutter build web`;
- `flutter build apk --debug`.

`flutter build macos` foi executado no host macOS, mas o CodeSign falhou por metadados `resource fork/Finder information` adicionados pelo File Provider/iCloud no bundle gerado. A limitação operacional está documentada em `docs/frontend/platforms.md`.

## Referências Consultadas

- SAP EWM Goods Receipt e Putaway: https://learning.sap.com/courses/exploring-business-processes-in-sap-ewm-for-sap-s-4hana-cloud-private-edition/processing-a-goods-receipt-in-sap-ewm
- SAP EWM Warehouse Tasks for Putaway: https://help.sap.com/docs/PRODUCT_ID/3d97bec9bf1649099384bb8167df3cf2/ffc7cb53ad377114e10000000a174cb4.html
- Microsoft Business Central Warehouse Put-aways: https://learn.microsoft.com/en-us/dynamics365/business-central/warehouse-how-to-put-items-away-with-warehouse-put-aways
- Microsoft Learn Receive and Put Away Items: https://learn.microsoft.com/en-us/training/modules/receive-put-away-items/
- Odoo Putaway Rules: https://www.odoo.com/documentation/15.0/applications/inventory_and_mrp/inventory/routes/strategies/putaway.html
- ERPNext Putaway Rule: https://docs.frappe.io/erpnext/putaway-rule
