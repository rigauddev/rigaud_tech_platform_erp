# Modules

Diretório dos módulos independentes do ERP.

Cada módulo segue DDD simplificado e Clean Architecture:

- `domain`: contratos e conceitos centrais do módulo.
- `application`: use cases e orquestração de aplicação.
- `infrastructure`: adaptadores externos e persistência futura.
- `presentation`: interfaces HTTP/API futuras.
- `tests`: testes isolados do módulo.

Módulos preparados nesta etapa:

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

Até DEV-006, `auth` e `companies` possuem fundações técnicas implementadas.

Os demais módulos permanecem reservados para Tasks futuras.
