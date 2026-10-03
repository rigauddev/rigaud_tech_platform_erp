# Restaurant

Módulo reservado para contexto de restaurante.

Estrutura independente preparada com camadas `application`, `domain`, `infrastructure`, `presentation` e `tests`.

`RESTAURANT-001` adiciona salões e mesas com camadas de domínio, aplicação, infraestrutura e apresentação. Pedidos, KDS, impressão, pagamento e produção permanecem em tasks futuras.
# Restaurant Backend Module

O módulo concentra o núcleo operacional de Restaurante. Nesta fase inclui salões, mesas e setores por filial, sempre resolvidos a partir do tenant e filial do token autenticado.

Setores são contextos operacionais (salão, varanda, bar, VIP e balcão); não substituem o mapa visual das mesas. Pedidos, KDS, impressão, PDV e produção permanecem fora deste escopo.
