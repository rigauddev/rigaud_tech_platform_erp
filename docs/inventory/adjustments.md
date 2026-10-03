# Stock Adjustments

REST-012 evolui o ajuste de estoque para uma operação rastreável. Todo ajuste gera um `InventoryMovement` confirmado e um registro `InventoryAdjustment`; nenhum saldo é editado fora desse fluxo.

## Motivos

Os motivos padronizados são `correction`, `damage`, `loss`, `expiry`, `opening_balance`, `return` e `reversal`. O texto livre continua obrigatório para contextualizar o fato operacional.

## Estorno

`POST /api/v1/inventory/adjustments/{adjustment_id}/reverse` gera um novo ajuste de sentido contrário e vincula-o ao ajuste original. Um ajuste só pode ser estornado uma vez. Não há edição, exclusão ou reversão direta do movimento original.

## Limites

O ajuste de saída respeita saldo disponível, incluindo reservas e quantidades pendentes de put away. Fluxos configuráveis de aprovação pertencem a uma futura task de RBAC configurável.

## Referências

- [Odoo Inventory Adjustments](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.html)
- [Microsoft Business Central: count, adjust and reclassify](https://learn.microsoft.com/dynamics365/business-central/inventory-how-count-adjust-reclassify)
- [ERPNext Stock Reconciliation](https://docs.frappe.io/erpnext/stock-reconciliation)
