# Products Troubleshooting

## Produto não encontrado

Confirme se o usuário autenticado pertence ao mesmo tenant do produto.

Produtos excluídos logicamente também retornam `PRODUCT_NOT_FOUND`.

## Código já cadastrado

`internal_code` deve ser único dentro da empresa.

O mesmo código pode existir em outro tenant.

Código retornado:

```text
PRODUCT_INTERNAL_CODE_ALREADY_EXISTS
```

## Código de barras já cadastrado

`barcode` é opcional.

Quando informado, deve ser único dentro da empresa.

Código retornado:

```text
PRODUCT_BARCODE_ALREADY_EXISTS
```

## Produto indisponível

Produto inativo não pode ser marcado como disponível para venda.

Ative o produto antes de alterar disponibilidade.
