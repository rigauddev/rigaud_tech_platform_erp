# Menu Do Dia E Disponibilidade Comercial

Disponibilidade de cardápio é uma decisão comercial de curto prazo: define o
que pode ser oferecido hoje, em qual filial, período e canal. Ela não é o saldo
físico de insumos.

`RESTAURANT-004` registra uma publicação por produto, filial, data e período,
com canais e cota opcional. O banco garante unicidade nesse escopo; a API
audita criação, edição e remoção lógica.

Separar disponibilidade comercial de estoque evita vender pratos ainda não
preparados e preserva o Inventory Engine como fonte de verdade dos saldos. A
integração automática com produção e receitas será feita somente na EPIC
Restaurant Production.
