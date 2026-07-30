# API Response Contract

Resposta padrão de sucesso:

```json
{
  "success": true,
  "code": "API_SUCCESS",
  "message": "Operação concluída com sucesso.",
  "data": {},
  "meta": null,
  "request_id": "uuid",
  "timestamp": "2026-07-30T00:00:00Z"
}
```

Durante transição, alguns campos de `data` também aparecem no topo para compatibilidade.
