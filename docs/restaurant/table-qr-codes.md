# QR Codes das Mesas

RESTAURANT-005 entrega a identificação digital segura de cada mesa. O QR Code contém uma URL pública com um token aleatório; não expõe identificadores internos, tenant, filial, usuário ou permissões.

## Operação

1. Acesse `Restaurante > QR Codes das mesas`.
2. Gere os códigos pendentes ou renove o código de uma mesa específica.
3. Selecione as mesas e prepare a impressão em folha A4.
4. Fixe o código físico na mesa.

Ao apontar a câmera, o endpoint público confirma somente o número, nome opcional e disponibilidade da mesa. O Cardápio Online será conectado na RESTAURANT-006; pedidos, pagamento e dados de cliente não são entregues por esta rota.

## API

| Método | Endpoint | Autenticação | Finalidade |
| --- | --- | --- | --- |
| `POST` | `/api/v1/restaurant/tables/{table_id}/qr-code` | necessária | gera ou rotaciona o token da mesa e audita a ação |
| `GET` | `/api/v1/restaurant/table-access/{qr_code}` | pública | resolve apenas o contexto mínimo da mesa ativa |

Renovar um QR Code invalida imediatamente o token anterior. Mesas inativas e mesas removidas não podem ser resolvidas publicamente.

## Limites desta task

- A tela apresenta formato de impressão e seleção; integração com impressora física pertence à task de KDS/impressão.
- Não há leitura por câmera, cardápio público, pedido, pagamento ou KDS nesta entrega.
- O QR não substitui autenticação de operadores no ERP.

## Ajuda ao usuário

O passo a passo operacional está em [Ajuda: QR Codes das mesas](../help/restaurant/table-qr-codes.md).
