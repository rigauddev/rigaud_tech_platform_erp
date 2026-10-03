# Receiving Documents

Feature de documentos de recebimento de mercadorias.

Mantem a chegada e conferencia planejada de produtos antes da etapa de movimentacao fisica do estoque.

Esta feature nao altera saldo e nao cria movimentacoes de estoque.

REST-008 adiciona confirmação física do recebimento.

Ao confirmar:

- o backend cria movimento de estoque;
- o saldo físico é atualizado;
- a quantidade fica pendente de put away;
- o produto ainda não fica disponível.
