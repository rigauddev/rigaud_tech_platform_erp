# Mesas e Mapa do Salão

`RESTAURANT-001` cria a base operacional de salões e mesas por filial.

## Contrato

- `RestaurantFloor` representa um salão ou mapa físico da filial.
- `RestaurantTable` pertence a um salão e possui número, capacidade, forma e coordenadas para o mapa.
- O número é único dentro do salão ativo; todos os registros são isolados por tenant e filial.
- Exclusões são lógicas e auditadas.
- QR Code é um identificador opcional reservado. Geração e leitura pertencem à `RESTAURANT-005`.
- `Sector` não é duplicado nesta etapa: a especialização entre salão, setor e ambiente será feita na `RESTAURANT-002`.

## Status preparados

| Status | Evolução responsável |
| --- | --- |
| `available`, `occupied`, `reserved`, `cleaning`, `blocked` | operação do salão |
| `order_pending`, `kitchen` | `RESTAURANT-007` e `RESTAURANT-008` |
| `waiting_payment` | `RESTAURANT-010` |

## API

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET`, `POST` | `/api/v1/restaurant/floors` | consultar e criar salões |
| `GET`, `PUT`, `DELETE` | `/api/v1/restaurant/floors/{id}` | administrar um salão |
| `GET`, `POST` | `/api/v1/restaurant/tables` | consultar e criar mesas; suporta `floor_id` |
| `GET`, `PUT`, `DELETE` | `/api/v1/restaurant/tables/{id}` | administrar uma mesa |

As rotas usam tenant e filial do contexto autenticado, envelope padrão, `request_id` e auditoria.

## Experiência Flutter

Em telas largas, o mapa usa as coordenadas da mesa e mostra detalhes em painel lateral. Em telas compactas, a mesma informação vira lista de cartões selecionáveis.

## Limites e próximos passos

Esta entrega não cria pedidos, pagamento, impressão, estação de preparo, disponibilidade de menu ou produção. Ficam registrados:

- `RESTAURANT-003` e `RESTAURANT-007`: experiência dedicada de atendimento do garçom na mesma base Flutter e backend;
- `RESTAURANT-008`: KDS e impressão na mesma fila por estação, com estados de fila, início e pronto/retirado; a estimativa combinará tempo médio configurável por item e carga da estação;
- `RESTAURANT-010`: o garçom poderá iniciar uma solicitação de pagamento, mas autorização, recebimento e fechamento pertencem ao Caixa/PDV;
- custo de matéria-prima e produção permanecem na `EPIC-RESTAURANT-PRODUCTION`.

## Referências

- [Flutter: adaptive and responsive design](https://docs.flutter.dev/ui/adaptive-responsive)
- [Odoo: Restaurant features](https://www.odoo.com/documentation/18.0/applications/sales/point_of_sale/restaurant.html)
- [FastAPI: response models](https://fastapi.tiangolo.com/tutorial/response-model/)
- [SQLAlchemy: asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
