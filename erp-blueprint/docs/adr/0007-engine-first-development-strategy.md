# ADR 0007: Estratégia Engine-First Para Módulos Comerciais

## Status

Aceita.

## Contexto

O projeto entra na fase de regras de negócio compartilhadas. Estoque, pedidos, restaurante, POS, financeiro e relatórios precisam escalar para Restaurante, Loja, Delivery, Marketplace e futuros segmentos.

Implementar cada funcionalidade como um módulo isolado por segmento criaria duplicação e alto custo de manutenção.

## Decisão

Adotar estratégia Engine-first para domínios comerciais reutilizáveis.

Cada engine deve seguir:

```text
DOC
    ↓
IMPLEMENTAÇÃO
    ↓
REVIEW
    ↓
INTEGRAÇÃO
```

A documentação congela domínio, eventos, fluxos, estados, integrações, offline strategy e limites.

A implementação cria backend, frontend, testes e documentação operacional.

A revisão estabiliza comportamento, segurança, performance e aderência arquitetural.

A integração conecta a engine aos demais módulos.

## Engines Planejadas

- ENGINE-001 — Inventory Engine;
- ENGINE-002 — Order Engine;
- ENGINE-003 — Restaurant Engine;
- ENGINE-004 — POS Engine;
- ENGINE-005 — Financial Engine;
- ENGINE-006 — Reporting Engine.

## Consequências

- REST-003 passa a implementar o Inventory Engine, não um estoque exclusivo de restaurante.
- REST e STORE consomem engines compartilhadas.
- Cada nova engine deve nascer demonstrável no Demo Environment.
- Eventos internos devem ser previstos antes de integrações externas.
- Kafka permanece futuro e substituível por dispatcher interno enquanto a arquitetura evolui.

