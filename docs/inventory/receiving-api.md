# Receiving API

Base path:

```text
/api/v1/receiving-documents
```

## Endpoints

- `GET /receiving-documents`
- `GET /receiving-documents/{document_id}`
- `POST /receiving-documents`
- `PUT /receiving-documents/{document_id}`
- `POST /receiving-documents/{document_id}/status`
- `DELETE /receiving-documents/{document_id}`

## Payload

```json
{
  "warehouse_id": "uuid",
  "supplier_id": null,
  "document_number": "NF-001",
  "document_type": "invoice",
  "status": "expected",
  "expected_date": null,
  "received_date": null,
  "notes": "Mercadoria aguardando conferencia.",
  "items": [
    {
      "product_id": "uuid",
      "ordered_quantity": "10.000",
      "received_quantity": "0.000",
      "damaged_quantity": "0.000",
      "unit_cost": "12.50"
    }
  ]
}
```

## Resposta

Todos os endpoints retornam o envelope padrão:

```text
success, code, message, data, meta, request_id, timestamp
```

## Mensagens

- `RECEIVING_DOCUMENT_CREATED`
- `RECEIVING_DOCUMENT_UPDATED`
- `RECEIVING_DOCUMENT_STATUS_CHANGED`
- `RECEIVING_DOCUMENT_DELETED`
- `RECEIVING_DOCUMENT_RETRIEVED`
- `RECEIVING_DOCUMENT_LIST_RETRIEVED`
- `RECEIVING_DOCUMENT_NOT_FOUND`
- `RECEIVING_DOCUMENT_NUMBER_ALREADY_EXISTS`
- `RECEIVING_DOCUMENT_BRANCH_REQUIRED`
- `RECEIVING_DOCUMENT_INVALID_DATA`
- `RECEIVING_DOCUMENT_ITEM_REQUIRED`
