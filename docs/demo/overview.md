# Demo Environment

DOC-003 cria o ambiente oficial de demonstração da Rigaud Tech Platform ERP.

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
make demo-restaurant
make demo-retail
make demo-all
```

Resetar apenas tenants operacionais de demonstração:

```bash
make demo-reset
```

`make demo-reset` remove `sabor-da-serra` e `moda-center`, mas preserva o tenant `rigaud-platform`.

O alvo `make test` executa o reset dos tenants operacionais demo antes do pytest. Isso evita que dados persistentes de demonstração interfiram nas fixtures de integração.

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
- 50 produtos demo.

Loja:

- empresa `Moda Center`;
- filiais `Shopping` e `Centro`;
- usuários demo para admin, gerente, vendedor, caixa e estoque;
- categorias `Calcados`, `Roupas`, `Bolsas` e `Acessorios`;
- 80 produtos demo.

## Limite Da DOC-003

Esta task não cria funcionalidades comerciais novas.

Como os módulos de estoque, mesas, clientes, pedidos, QR Code, delivery, caixa e vendas ainda não existem no `develop`, os cenários operacionais completos ficam documentados em `docs/demo/scenario-engine.md` para implementação incremental nas próximas tasks.
