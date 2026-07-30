# Request Context

Toda requisição recebe `request_id`.

O cliente pode enviar `X-Correlation-ID`, desde que seja curto e válido.

Respostas incluem:

- `X-Request-ID`
- `X-Correlation-ID`, quando informado

O contexto usa `contextvars` e é limpo ao final da requisição.
