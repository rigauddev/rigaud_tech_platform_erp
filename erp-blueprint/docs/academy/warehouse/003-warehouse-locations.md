# Academy: Warehouse Locations

Warehouse Location é o endereço físico do estoque.

Ela fica abaixo da zona:

```text
Warehouse
  -> Zone
  -> Location
```

Exemplos:

- `ALM-A01`;
- `CAM-001`;
- `VIT-001`;
- `EXP-A01`.

## Por Que Separar Zone E Location

A zona descreve a função operacional, como recebimento, armazenagem ou expedição.

A localização descreve onde o item fica fisicamente.

Essa separação prepara o ERP para:

- múltiplos depósitos;
- endereçamento por prateleira;
- QR Code;
- código de barras;
- picking;
- put away;
- inventário;
- Visual Warehouse futuro.

## Limite Da REST-006

A REST-006 cadastra a localização e prepara a rastreabilidade.

Ela não movimenta estoque, não lê QR Code pela câmera e não implementa mapa visual.
