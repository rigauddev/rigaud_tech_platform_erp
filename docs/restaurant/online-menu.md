# Cardápio Online

RESTAURANT-006 apresenta ao cliente o cardápio publicado para uma mesa por
meio do QR Code. A experiência é pública e somente de leitura: exibe nome,
descrição, foto, preço, período de serviço e disponibilidade do item.

## Preparar o cardápio

1. Cadastre ou atualize o produto, incluindo preço, descrição e imagem quando
   disponíveis.
2. Em `Restaurante > Cardápio`, publique a disponibilidade para a filial e a
   data de serviço, selecione o período e inclua o canal `qr`.
3. Confirme que o produto, a filial e a mesa estão ativos.
4. Em `Restaurante > QR Codes das mesas`, gere o código da mesa.
5. Leia o QR Code com um celular para abrir o cardápio público.

Os itens exibidos são filtrados pela filial e pela data local da filial. O
backend só apresenta disponibilidades publicadas, ativas e marcadas para o
canal `qr`; produtos inativos, removidos ou não disponíveis para venda são
excluídos. Uma cota comercial esgotada aparece como indisponível.

## Acesso em Web e Desktop

No Flutter Web, o QR Code usa a origem do navegador em que o ERP está aberto.
Para gerar QR Codes pelo cliente Desktop, informe a URL pública do frontend no
build:

```bash
flutter build windows --dart-define=PUBLIC_APP_URL=https://erp.exemplo.com
```

Use uma URL alcançável pelo celular do cliente, não `localhost`. Se o Desktop
não tiver `PUBLIC_APP_URL`, a tela informa que falta configurar o endereço e
não mostra um QR que levaria a um destino inválido. A URL da API continua
configurada separadamente por `API_BASE_URL`.

## API pública

`GET /api/v1/restaurant/public/menu/{qr_code}` resolve o QR Code ativo, obtém a
data pelo fuso horário da filial e devolve somente o contexto público da mesa
e os itens elegíveis. A resposta não inclui tenant, identificadores internos
de produto, custo, códigos internos, dados de usuários ou informações de
outras filiais.

## Limites da RESTAURANT-006

- O cardápio não cria pedidos e não oferece checkout, pagamento ou captura de
  dados do cliente.
- O cliente deve falar com a equipe para fazer o pedido; pedido, notificação
  ao garçom e roteamento para cozinha pertencem à RESTAURANT-007.
- KDS, impressão de produção e impressoras fiscais não fazem parte desta
  entrega.
- A quantidade vendável continua sendo uma cota comercial, separada do saldo
  físico e de produção.

## Referências de experiência

- [Odoo — Self-ordering](https://www.odoo.com/documentation/saas-18.4/applications/sales/point_of_sale/self_order.html)
- [ERPNext — Restaurant Order Entry](https://docs.frappe.io/erpnext/order-entry)

As referências orientam a entrada simples via QR e a leitura do menu no
celular; fluxos de pedido ou pagamento dessas plataformas não são copiados
para esta task.

## Guias

- [Ajuda: Cardápio Online](../help/restaurant/online-menu.md)
- [Academy: Cardápio Online](../../erp-blueprint/docs/academy/restaurant/007-cardapio-online.md)
