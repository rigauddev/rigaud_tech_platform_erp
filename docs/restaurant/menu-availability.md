# Menu Do Dia E Disponibilidade Comercial

> A DOC-011 mantém este contrato como parte do Restaurant Operations Core. Esta publicação comercial não cria saldo físico nem baixa insumos.

`RESTAURANT-004` publica itens do catálogo de Produtos para uma filial, data e
período de serviço. A equipe informa diariamente quais pratos podem ser
vendidos e, quando aplicável, a quantidade máxima comercializável.

## API

- `GET /api/v1/restaurant/menu-availabilities?service_date=&service_period=`
- `GET /api/v1/restaurant/menu-availabilities/{id}`
- `POST /api/v1/restaurant/menu-availabilities`
- `PUT /api/v1/restaurant/menu-availabilities/{id}`
- `DELETE /api/v1/restaurant/menu-availabilities/{id}`

O backend resolve tenant e filial pelo token. Um mesmo produto só pode ser
publicado uma vez por filial, data e período. As ações são auditadas e a
remoção é lógica.

## Regra Operacional Do MVP

1. Gerente, cozinha ou usuario autorizado abre o Menu do Dia.
2. Seleciona produto/prato, status e quantidade vendavel opcional.
3. Publica o cardápio para um ou mais canais de venda.
4. Cliente acessa o QR Code da mesa e ve somente itens publicados.
5. Ao enviar o pedido, o sistema associa mesa, cliente e garcom responsavel.
6. O pedido chega ao garcom responsavel e e roteado para a impressora ou estacao de cozinha configurada.

Um item fica indisponível quando estiver inativo, fora do período publicado,
com a cota comercial esgotada ou bloqueado por regra futura de
estoque/produção. O cliente nunca poderá comprar acima da quantidade publicada.

## Interface

A tela `Restaurante > Cardápio` segue o canvas aprovado: filtros operacionais,
indicadores de itens publicados, disponíveis, cotas limitadas e esgotados, além
da tabela de disponibilidade comercial. Ela usa o catálogo PT/EN e carrega
produtos e disponibilidade pela API real.

## Limites Arquiteturais

`menu_available_quantity` nao e saldo de estoque e nao substitui `InventoryBalance`. No MVP ele e uma cota comercial diaria, mantida no Restaurant Engine e auditada. A futura EPIC Restaurant Production podera sugerir ou limitar essa cota conforme producao confirmada, receita, insumos, perdas e capacidade da cozinha.

Não implementa baixa automática de insumos, ficha técnica, custo de produção,
pedido, KDS ou previsão. Esses itens pertencem à EPIC-RESTAURANT-PRODUCTION e
às próximas tasks do MVP Restaurante.
