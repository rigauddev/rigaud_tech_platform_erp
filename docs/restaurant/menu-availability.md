# Disponibilidade Diaria Do Cardapio

O cardapio online mostra somente itens publicados e disponiveis para a filial e o periodo de servico atual. A equipe informa diariamente quais pratos podem ser vendidos e, quando aplicavel, a quantidade maxima comercializavel.

## Regra Operacional Do MVP

1. Gerente, cozinha ou usuario autorizado abre o Menu do Dia.
2. Seleciona produto/prato, status e quantidade vendavel opcional.
3. Publica o cardapio para um ou mais setores, canais ou mesas.
4. Cliente acessa o QR Code da mesa e ve somente itens publicados.
5. Ao enviar o pedido, o sistema associa mesa, cliente e garcom responsavel.
6. O pedido chega ao garcom responsavel e e roteado para a impressora ou estacao de cozinha configurada.

Um item fica indisponivel quando estiver inativo, fora do periodo publicado, sem quantidade comercial disponivel ou bloqueado por regra futura de estoque/producao. O cliente nunca pode comprar acima da quantidade publicada.

## Limites Arquiteturais

`menu_available_quantity` nao e saldo de estoque e nao substitui `InventoryBalance`. No MVP ele e uma cota comercial diaria, mantida no Restaurant Engine e auditada. A futura EPIC Restaurant Production podera sugerir ou limitar essa cota conforme producao confirmada, receita, insumos, perdas e capacidade da cozinha.

Nao implementa baixa automatica de insumos, ficha tecnica, custo de producao ou previsao. Esses itens pertencem a EPIC-RESTAURANT-PRODUCTION.
