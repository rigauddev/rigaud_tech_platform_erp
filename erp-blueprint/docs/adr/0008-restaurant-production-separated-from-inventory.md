# ADR 0008: Produção Do Restaurante Separada Do Estoque

## Status

Aceita.

## Contexto

O ERP precisa atender restaurante, varejo e futuras verticais usando o mesmo núcleo de estoque.

Produção de restaurante envolve receitas, planejamento, cozinha, desperdício, previsão e consumo de insumos. Misturar essa lógica diretamente no Inventory Engine criaria acoplamento entre estoque físico e processo produtivo.

## Decisão

Manter produção de restaurante em uma EPIC futura chamada `EPIC-RESTAURANT-PRODUCTION`.

Escopo planejado:

- Recipe Engine;
- Production Planning;
- Daily Production;
- Kitchen Production;
- Consumption;
- Waste;
- Forecast;
- AI Insights.

O Inventory Engine continuará responsável por saldos e movimentações.

Quando a produção for implementada, consumo de ingredientes e perdas serão registrados por `InventoryMovement`, usando:

```text
origin_module=RESTAURANT_PRODUCTION
business_process=PRODUCTION
```

## Consequências

- REST-009 implementa Put Away sem criar produção.
- Pratos não serão tratados como saldo físico direto.
- Receitas e planejamento pertencem ao domínio Restaurant Production.
- Auditoria, relatórios e IA poderão diferenciar compra, put away, produção, venda, perda e inventário por `origin_module` e `business_process`.
- O núcleo permanece compatível com SaaS, On-Premise e futuras integrações com POS, Delivery e Marketplace.
