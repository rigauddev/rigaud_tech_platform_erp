# Products

Módulo responsável pelo cadastro de produtos compartilhado pelo Core e pelo MVP Restaurante.

Camadas:

- `domain`: enums, exceções e contrato de repositório.
- `application`: validações e use cases.
- `infrastructure`: modelo SQLAlchemy e repositório.
- `presentation`: schemas e router FastAPI.
- `tests`: estrutura local reservada.

A REST-001 implementa somente Produtos. Categorias, estoque, ingredientes, variações, cardápio, pedidos, fiscal e caixa ficam fora do escopo.
