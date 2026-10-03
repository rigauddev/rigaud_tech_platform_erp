# Garçons e Equipe

`RESTAURANT-003` registra a equipe operacional da filial: garçons, atendentes e gestores. O perfil operacional pode apontar para um usuário de autenticação e para um setor padrão, mas não substitui RBAC nem cria uma escala de trabalho.

## API

- `GET /api/v1/restaurant/staff`
- `GET /api/v1/restaurant/staff/{id}`
- `POST /api/v1/restaurant/staff`
- `PUT /api/v1/restaurant/staff/{id}`
- `DELETE /api/v1/restaurant/staff/{id}`

Cada operação é isolada por tenant e filial ativa, usa o envelope padrão e registra auditoria.

## Limites

O status atual (`available`, `serving`, `paused` e `offline`) organiza a leitura operacional. Turnos, distribuição formal de mesas, pedidos, impressão e pagamento serão implementados nas tasks específicas seguintes.

## Interface

A tela segue a referência visual aprovada: navegação contextual, topo com busca, indicadores, cartões por profissional e tabela pesquisável. A mesma composição é responsiva, com cartões em telas menores.
