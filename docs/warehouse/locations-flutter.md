# Warehouse Locations Flutter

Feature:

```text
erp-platform/frontend/lib/features/warehouse_locations/
```

Arquitetura:

- `domain`;
- `data`;
- `presentation`.

## Telas

- lista;
- cadastro;
- edição;
- detalhe.

## Recursos

- Riverpod para estado;
- Repository Pattern;
- DataSource HTTP com Dio;
- filtros por depósito, zona e pesquisa;
- ações de ativar, inativar, remover e reordenar.

## Multiplataforma

A implementação usa apenas Flutter Material, Riverpod, GoRouter e Dio já existentes no projeto. Não adiciona plugin específico de câmera, QR Code ou código de barras nesta task, preservando compatibilidade Web, Android, iOS, Windows, Linux e macOS.
