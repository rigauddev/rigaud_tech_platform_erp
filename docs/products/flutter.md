# Products Flutter

A feature Flutter de Products segue Feature First, MVVM simplificado e Riverpod.

Estrutura:

```text
lib/features/products/
  data/
  domain/
  presentation/
```

Telas:

- lista de produtos;
- cadastro;
- edição;
- detalhe.

A UI possui layout responsivo com tabela em telas largas e cards em telas menores.

Mensagens de erro usam o envelope padronizado da API e preservam `request_id` quando disponível no erro mapeado pelo cliente HTTP.

## Plataformas

Preparado para:

- Web;
- Android;
- iOS;
- macOS;
- Windows.

Windows permanece preparado, mas não validado em macOS.
