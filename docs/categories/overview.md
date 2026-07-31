# Categories Overview

REST-002 cria Categorias de Produtos como módulo compartilhado do Core.

O módulo atende Restaurante, Loja de Roupas, Calçados, Acessórios e segmentos futuros.

## Responsabilidades

- cadastrar categorias por tenant;
- organizar categorias em hierarquia sem limite fixo de profundidade;
- manter slug único por tenant;
- manter código interno único por tenant;
- ativar e desativar categorias;
- ordenar manualmente;
- remover com soft delete;
- registrar auditoria.

## Fora do Escopo

- estoque;
- cardápio;
- delivery;
- vínculo obrigatório com produtos;
- presets automáticos por segmento;
- drag and drop funcional.

## Form Blueprint

O módulo já documenta o conceito de Form Blueprint para futuros cadastros reutilizáveis.

Exemplos planejados:

- Restaurante: Bebidas, Pratos, Sobremesas.
- Loja: Camisetas, Calças, Tênis, Bolsas.

A carga automática de presets fica para uma task futura.
