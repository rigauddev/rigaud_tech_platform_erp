# Inventory Count

Uma contagem fisica e um documento de verificacao, nao uma edicao de saldo. O ERP registra o saldo esperado ao criar os itens e so cria movimentos `count` ao finalizar todas as quantidades observadas.

Isso preserva a trilha de auditoria, permite investigar divergencias e impede que o cancelamento altere o estoque. A projection `InventoryBalance` continua derivada dos movimentos confirmados.
