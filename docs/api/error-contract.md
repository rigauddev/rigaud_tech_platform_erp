# API Error Contract

Resposta padrão de erro:

```json
{
  "success": false,
  "code": "VALIDATION_ERROR",
  "message": "Existem dados inválidos na requisição.",
  "errors": [],
  "request_id": "uuid",
  "timestamp": "2026-07-30T00:00:00Z"
}
```

Mensagens internas, SQL e stack traces não são retornados.
