# Demo Environment & Scenario Engine

DOC-003 cria o ambiente oficial de demonstração, homologação e cenários da Rigaud Tech Platform ERP.

O objetivo é permitir que qualquer pessoa suba a stack e carregue dados realistas sem cadastrar tudo manualmente.

## Comandos

Subir a stack:

```bash
make up
```

Aplicar todo o ambiente demo:

```bash
make demo
```

Aplicar datasets separados:

```bash
make demo-platform
make demo-users
make demo-restaurant
make demo-retail
make demo-scenarios
make demo-all
```

Resetar apenas tenants operacionais de demonstração:

```bash
make demo-reset
```

Aliases operacionais:

```bash
make restaurant
make retail
make scenarios
make reset-demo
```

Playground completo:

```bash
make playground
```

Esse comando sobe Docker, aplica migrations, instala dados demo, consulta cenários e tenta abrir Flutter, Swagger e documentação no navegador local.

Scripts equivalentes:

- `scripts/demo.py`
- `scripts/demo_reset.py`
- `scripts/demo_users.py`
- `scripts/demo_restaurant.py`
- `scripts/demo_store.py`
- `scripts/demo_scenarios.py`

`make demo-reset` remove `sabor-da-serra` e `moda-center`, mas preserva o tenant `rigaud-platform`.

O alvo `make test` executa o reset dos tenants operacionais demo antes do pytest. Isso evita que dados persistentes de demonstração interfiram nas fixtures de integração.

## Demo API

Endpoints disponíveis somente em `local`, `development` e `test`:

- `GET /api/v1/demo/status`
- `GET /api/v1/demo/install`
- `GET /api/v1/demo/reset`
- `GET /api/v1/demo/scenarios`

Em produção, esses endpoints retornam `DEMO_NOT_AVAILABLE`.

## Demo Dashboard

O Flutter possui a rota `/demo`, exibida no menu somente fora de produção.

Na DOC-003, ela permite visualizar status, instalar dados demo, atualizar o status e resetar os tenants operacionais demo.

## Dados Criados

Platform:

- tenant `rigaud-platform`;
- administrador da plataforma;
- contas de suporte, financeiro e comercial.

Restaurante:

- empresa `Restaurante Sabor da Serra`;
- filiais `Matriz`, `Delivery` e `Food Truck`;
- usuários demo para admin, gerente, caixa, garçons, cozinha, estoque e financeiro;
- categorias `Bebidas`, `Entradas`, `Pratos`, `Sobremesas` e `Promocoes`;
- depósitos `Deposito Principal`, `Camara Fria`, `Bar`, `Cozinha`, `Expedicao Delivery` e `Estoque Food Truck`;
- zonas `Recebimento`, `Almoxarifado`, `Camara Fria`, `Producao` e `Expedicao`;
- localizações `REC-A01`, `ALM-A01`, `CAM-001`, `COZ-PREP` e `EXP-RET`;
- 50 produtos demo.

Loja:

- empresa `Moda Center`;
- filiais `Shopping` e `Centro`;
- usuários demo para admin, gerente, vendedor, caixa e estoque;
- categorias `Calcados`, `Roupas`, `Bolsas` e `Acessorios`;
- depósitos `Estoque`, `Vitrine`, `Reserva` e `Estoque Centro`;
- zonas `Recebimento`, `Vitrine`, `Reserva` e `Expedicao`;
- localizações `REC-A01`, `VIT-001`, `RES-A01` e `EXP-A01`;
- 80 produtos demo.

## Limite Da DOC-003

Esta task não cria funcionalidades comerciais novas.

Como os módulos de mesas, clientes, pedidos, QR Code, delivery, caixa e vendas ainda não existem no `develop`, os cenários operacionais completos ficam documentados em `docs/demo/scenario-engine.md` para implementação incremental nas próximas tasks.

## Princípio

Tudo que for desenvolvido deve ser demonstrável.

Cada módulo novo deve, ao final da sua task, registrar dados demo, cenários, testes, documentação Academy e integração futura com o Demo Dashboard quando aplicável.
