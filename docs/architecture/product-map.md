# Product Map

Mapa vivo do produto Rigaud Tech Platform ERP.

Este mapa representa o produto planejado e nao significa que todas as funcionalidades ja estejam implementadas.

## Status

- `Implementado`: ja existe codigo funcional.
- `Em desenvolvimento`: existe base, task em andamento ou modulo parcialmente entregue.
- `Planejado`: entra em roadmap proximo.
- `Futuro`: direcao arquitetural sem implementacao prevista imediata.

## Mapa

```text
RIGAUD TECH PLATFORM ERP
│
├── Gestão Empresarial
│   ├── Empresas [Implementado]
│   ├── Filiais [Implementado]
│   ├── Usuários [Implementado]
│   ├── Perfis [Planejado]
│   ├── Permissões [Planejado]
│   └── Departamentos [Futuro]
│
├── Produtos [Implementado]
│
├── Categorias [Implementado]
│
├── Estoque [Em desenvolvimento]
│   ├── Depósitos [Implementado]
│   ├── Zonas [Implementado]
│   ├── Localizações [Implementado]
│   ├── Recebimento [Implementado]
│   ├── Goods Receipt [Implementado]
│   ├── Put Away [Em desenvolvimento]
│   └── Inventário [Em desenvolvimento]
│
├── Restaurante [Em desenvolvimento]
│   ├── Gestão no app principal [Planejado]
│   ├── Mesas [Planejado]
│   ├── Garçons [Planejado]
│   ├── App operacional de garçom [Planejado]
│   ├── Menu do Dia e Disponibilidade [Planejado]
│   ├── Cardápio [Planejado]
│   ├── QR Code [Planejado]
│   ├── App/portal do cliente [Planejado]
│   ├── Pedidos e Garçom Responsável [Planejado]
│   ├── Cozinha, KDS e Impressão [Planejado]
│   ├── PDV / Caixa [Planejado]
│   ├── Entrada por NF-e/XML [Planejado]
│   └── Produção [Futuro]
│
├── Financeiro [Planejado]
│   ├── Contas a pagar [Planejado]
│   ├── Contas a receber [Planejado]
│   ├── Caixa [Planejado]
│   ├── Bancos [Planejado]
│   └── Fluxo de caixa [Planejado]
│
├── Recursos Humanos [Futuro]
│   ├── Funcionários [Futuro]
│   ├── Departamentos [Futuro]
│   ├── Escalas [Futuro]
│   ├── Ponto [Futuro]
│   └── Férias [Futuro]
│
├── Produção [Futuro]
│   ├── Produtos [Futuro]
│   ├── Insumos [Futuro]
│   ├── Receitas/BOM [Futuro]
│   ├── Ordens de produção [Futuro]
│   ├── Consumo [Futuro]
│   └── Custos [Futuro]
│
├── Analytics [Futuro]
│
├── AI / MCP [Futuro]
│
└── Administração
    ├── Assinatura [Planejado]
    ├── Módulos [Planejado]
    ├── Integrações [Futuro]
    └── Deployment [Planejado]
```

## Direcoes Congeladas

- Production Engine deve ser independente do Restaurant.
- Restaurant utilizara Inventory e Production.
- Financial integrara Sales, Inventory, Restaurant e Production.
- HR sera independente, mas integrado a Users, Company e Branch.
- Quem realizou o pedido nao e necessariamente quem e responsavel pela mesa.
- Disponibilidade diaria de cardapio e cota comercial, separada do saldo fisico e da producao.
- AI/MCP consumira contexto e eventos respeitando tenant, filial, permissoes, auditoria e seguranca.
- Restaurant Operations é um núcleo configurável por filial e segmento; as experiências de gestão, garçom, KDS, PDV e cliente reutilizam o mesmo backend e base Flutter.

## Atualizacao

Este documento deve ser atualizado quando uma task alterar status, escopo, nome de modulo ou dependencia relevante.
