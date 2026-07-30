# Responsive Design

O frontend usa breakpoints compartilhados:

- Mobile: `0` a `599`
- Tablet: `600` a `1023`
- Desktop: `1024` a `1439`
- Large desktop: `1440+`

## Diretrizes

- Mobile deve respeitar `SafeArea` e teclado virtual.
- Desktop deve preparar menu lateral, barra superior, mouse e teclado.
- Componentes devem evitar tamanhos exagerados em telas grandes.
- Telas devem reutilizar `ResponsiveLayout` e `AppScaffold`.

Esta task cria apenas a base responsiva, sem fluxos funcionais do ERP.
