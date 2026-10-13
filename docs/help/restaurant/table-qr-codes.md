# QR Codes das Mesas

## Para que serve

O QR Code identifica uma mesa no atendimento digital. Ele prepara o acesso do cliente ao cardápio online, sem mostrar dados da empresa, do caixa ou de outros clientes.

## Como gerar

1. Entre em `Restaurante`.
2. Abra `QR Codes das mesas`.
3. Use `Gerar QR Codes` para criar os que estiverem pendentes ou abra o menu da mesa para renovar apenas um código.
4. Escolha `Visualizar cardápio` para testar a página pública da mesa dentro do ERP.
5. Selecione as mesas desejadas e escolha `Imprimir selecionados`.

## Quando renovar

Renove o QR Code quando a etiqueta for perdida, danificada ou quando houver necessidade de invalidar uma cópia antiga. Após a renovação, somente o novo código funciona.

## Problemas comuns

| Situação | O que fazer |
| --- | --- |
| A mesa aparece sem QR | Gere o código na tela de QR Codes. |
| O código não abre | Confirme que a mesa está ativa e que o dispositivo alcança a URL pública do ERP; se necessário, renove o código. |
| O cliente não vê o cardápio | Confirme que há itens publicados para a data atual e que o canal `qr` foi selecionado. |
| O QR do aplicativo Desktop não aparece | Configure `PUBLIC_APP_URL` com a URL do frontend acessível pelo celular. |

## Permissões

Somente operadores autorizados do restaurante podem gerar ou renovar códigos.
A consulta feita pelo QR é pública e retorna o cardápio publicado e o contexto
mínimo da mesa, sem dados internos de gestão. Para pedir, fale com a equipe.
