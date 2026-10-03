# Setores e Ambientes

`RESTAURANT-002` organiza os ambientes operacionais por filial: salão, varanda, bar, área VIP, balcão ou outro setor configurado.

Um setor pode apontar para um mapa de salão já criado, mas não substitui o mapa: o salão continua guardando a disposição visual das mesas e o setor define o contexto operacional que será usado por atendimento, garçom e cozinha nas etapas seguintes.

## API

- `GET /api/v1/restaurant/sectors`
- `GET /api/v1/restaurant/sectors/{id}`
- `POST /api/v1/restaurant/sectors`
- `PUT /api/v1/restaurant/sectors/{id}`
- `DELETE /api/v1/restaurant/sectors/{id}`

As operações usam tenant e filial do token, auditoria e envelope padrão.

## Experiência

A tela segue a composição visual aprovada: resumo operacional, cartões de ambientes e tabela de organização. Em telas menores, os mesmos cartões aparecem em lista, preservando leitura e toque.

O padrão de tela estabelece a base visual das próximas experiências de Restaurante: título orientado ao contexto, indicadores operacionais, cartões de leitura rápida e lista adaptativa. Ele não altera retrospectivamente telas fora desta task.

Pedidos, atribuição de garçom, KDS, impressão e PDV não são criados por esta task.
