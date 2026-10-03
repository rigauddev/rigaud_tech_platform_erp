# Transferências de Estoque

Uma transferência não é um ajuste de saldo. Ela é um documento operacional com duas confirmações: expedição e recebimento.

Na REST-013, a solicitação registra a intenção; o despacho gera uma saída imutável na origem; e o recebimento gera uma entrada imutável no destino. Isso permite rastrear estoque em trânsito sem alterar diretamente `InventoryBalance` por uma tela ou integração.

O processo fica restrito ao mesmo tenant e respeita a filial ativa em cada etapa. Divergências, recebimento parcial, transportadora, rota e lotes ficam para evoluções do WMS.
