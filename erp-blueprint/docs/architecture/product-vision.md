# Visão de Produto

A Rigaud Tech Platform ERP é uma plataforma ERP modular, multi-tenant e multiplataforma.

## Núcleo

O Rigaud Core concentra capacidades compartilhadas:

- Autenticação.
- Empresas.
- Usuários.
- Produtos.
- Categorias.
- Estoque.
- Clientes.
- Vendas.
- Caixa.
- Financeiro.
- Auditoria.
- Configurações.

## Restaurante

Fluxo do MVP Restaurante:

```text
Gerente
    ↓
Define o Menu do Dia
    ↓
Estoque controla disponibilidade
    ↓
Cardápio é publicado
    ↓
Cliente lê QR Code
    ↓
Realiza pré-cadastro
    ↓
Continua no Web ou utiliza App
    ↓
Escolhe produtos
    ↓
Adiciona observações
    ↓
Envia pedido
    ↓
Pedido chega à cozinha
    ↓
Garçom acompanha a mesa
    ↓
Cliente pode chamar o garçom responsável
    ↓
Pagamento
    ↓
Cupom ou NFC-e
```

Regras já definidas:

- Estoque controla disponibilidade do cardápio.
- Produtos sem estoque devem ficar indisponíveis.
- Cliente pode utilizar Web ou aplicativo.
- Pedido pode conter observações.
- Cada mesa pode possuir um garçom responsável.
- Cliente pode chamar o garçom.
- Garçom deve receber notificação.
- KDS recebe os pedidos da cozinha.
- Emissão fiscal permanece isolada.

## Loja de Roupas

Fluxo principal planejado:

```text
Vendedor
    ↓
Cria pré-venda
    ↓
Reserva produto
    ↓
Cliente realiza pagamento
    ↓
Pré-venda é convertida em venda
    ↓
Cupom ou NFC-e opcional
```

A Loja deve reutilizar o máximo possível do Core.
