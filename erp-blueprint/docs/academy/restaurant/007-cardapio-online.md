# Cardápio Online via QR Code

## Objetivo de aprendizagem

Entender como a publicação comercial da RESTAURANT-004, o QR da
RESTAURANT-005 e a experiência pública da RESTAURANT-006 compõem a consulta
do cardápio por mesa.

## Caminho do cliente

```text
QR ativo da mesa
    -> rota pública Flutter
    -> GET /api/v1/restaurant/public/menu/{qr_code}
    -> validação do token, empresa e filial
    -> itens publicados para a data, período e canal qr
    -> visualização de nome, descrição, imagem, preço e disponibilidade
```

## Regras de publicação

- Produto e disponibilidade devem estar ativos e publicados.
- O canal `qr` precisa estar incluído na disponibilidade comercial.
- A data é calculada no fuso horário da filial.
- Itens esgotados são exibidos sem permitir compra.
- Descrição e imagem são opcionais; o cardápio usa uma apresentação
  alternativa quando não há imagem.
- A API pública não retorna custo, códigos internos, UUID de produtos,
  identificadores do tenant ou dados de usuários.

## Limites operacionais

Esta experiência é somente de consulta. Ela não registra seleção, pedido,
pagamento ou cadastro de cliente. A RESTAURANT-007 será responsável pelo
pedido, pelo aviso ao garçom e pelo roteamento para preparo.

No Web, a URL pública é obtida da origem do navegador. Em build Desktop, defina
`PUBLIC_APP_URL` para o endereço do frontend que os celulares podem alcançar.

## Referências de UX consultadas

- [Odoo — Self-ordering](https://www.odoo.com/documentation/saas-18.4/applications/sales/point_of_sale/self_order.html)
- [ERPNext — Restaurant Order Entry](https://docs.frappe.io/erpnext/order-entry)

As referências sustentam o acesso por QR e o foco em leitura móvel; a task
não antecipa fluxo de pedidos ou pagamento.
