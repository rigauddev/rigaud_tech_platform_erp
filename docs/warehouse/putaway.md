# Warehouse Put Away

REST-009 conclui o primeiro fluxo físico de entrada no warehouse.

## Fluxo

```text
Warehouse
  -> Zone
  -> Location
  -> Put Away
  -> Saldo Disponível
```

O Put Away move mercadoria que já foi recebida fisicamente para uma localização final.

## Operação

A confirmação exige:

- documento de recebimento;
- produto;
- localização;
- quantidade;
- motivo opcional.

O backend valida tenant, filial, warehouse e localização ativa.

## Limite Do Escopo

REST-009 não implementa:

- sugestão automática de localização;
- regras de capacidade;
- FEFO/FIFO/LIFO;
- leitura real de QR Code ou código de barras;
- mobile scanner;
- produção de restaurante.

Esses recursos permanecem planejados para tasks futuras.
