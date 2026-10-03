# Academy: Categorias de Produtos

REST-002 introduz Categories como módulo compartilhado do Core.

## Por que Categories é Core

Categorias não pertencem apenas ao Restaurante.

O mesmo conceito serve para:

- Restaurante;
- Loja de Roupas;
- Calçados;
- Acessórios;
- segmentos futuros.

## Decisões Técnicas

- `tenant_id` isola categorias por empresa.
- `parent_id` permite árvore sem profundidade fixa.
- slug e código interno são únicos por tenant.
- exclusão é lógica.
- routers apenas orquestram use cases.
- auditoria registra eventos relevantes.

## Form Blueprint

Categorias inauguram a diretriz de Form Blueprint.

A task documenta a intenção, mas não implementa presets automáticos.

Presets por segmento serão tratados em epic futura.
