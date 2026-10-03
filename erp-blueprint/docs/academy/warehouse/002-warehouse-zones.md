# Academy — Warehouse Zones

Warehouse Zone é a camada operacional entre depósito e localização física.

Ela evita que o depósito vire uma lista plana de endereços e prepara o ERP para operações maiores.

## Estrutura

```text
Filial
  ↓
Warehouse
  ↓
Zone
  ↓
Stock Location
```

## Exemplos

Restaurante:

- Recebimento;
- Câmara Fria;
- Cozinha;
- Bar;
- Expedição.

Varejo:

- Recebimento;
- Vitrine;
- Reserva;
- Expedição.

## Por Que Separar Zone De Location

Zone representa intenção operacional.

Location representa endereço físico.

Exemplo:

```text
Zone: Câmara Fria
Location: CAM-001
```

Essa separação facilita relatórios, picking, contagem, transferências e permissões futuras.
