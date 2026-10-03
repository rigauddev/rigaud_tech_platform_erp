# ERP Glossary

Glossário oficial do domínio Rigaud Tech Platform ERP.

## Core

`Tenant`: limite lógico de dados de uma empresa. No projeto, é `Company`.

`Company`: empresa raiz do tenant.

`Deployment`: ambiente tecnico onde o ERP executa, podendo ser Cloud, On-Premise ou Hybrid.

`CLOUD_SHARED`: deployment SaaS compartilhado por varios tenants.

`CLOUD_DEDICATED`: deployment cloud dedicado para um tenant ou grupo controlado.

`ON_PREMISE`: deployment local no ambiente do cliente.

`HYBRID`: deployment local com sincronizacao futura para Rigaud Cloud.

`Deployment Stamp`: unidade repetivel de infraestrutura usada para escalar tenants e isolar grupos de clientes.

`Branch`: filial operacional de uma empresa.

`Active Branch`: filial operacional única ativa do usuário autenticado.

`Membership`: vínculo legado/compatível usado para contexto e permissões até a consolidação de RBAC.

`Work Assignment`: lotação operacional de um usuário em uma filial, com início, fim e histórico.

`Branch History`: trilha de auditoria para mudanças de filial ativa.

`Active Context`: empresa, filial e papel ativos resolvidos pelo backend para a sessão autenticada.

`Feature Flag`: chave que habilita ou desabilita comportamento.

`Entitlement`: direito de uso derivado de plano, assinatura ou regra comercial.

`Partner`: parceiro comercial ou operacional da Rigaud Tech, sem ser tenant.

`Reseller`: revendedor que atende clientes, sem substituir a empresa tenant.

`Sync Gateway`: componente futuro responsavel por sincronizar eventos e dados selecionados entre servidor local e cloud.

## Auth

`JWT`: token assinado usado para autenticação curta.

`Refresh Token`: token opaco usado para renovar sessão.

`MFA`: autenticação em dois fatores.

`TOTP`: código temporário gerado por aplicativo autenticador.

`RBAC`: controle de acesso baseado em papéis.

`Profile`: perfil funcional único do usuário, origem das permissões efetivas.

## Inventory

`Inventory Engine`: engine compartilhada de estoque.

`Warehouse`: unidade lógica de estoque dentro de uma filial.

`Warehouse Zone`: zona operacional dentro de um warehouse, como recebimento, armazenagem, produção, picking, expedição ou quarentena.

`Warehouse Location`: local físico dentro de uma zona de depósito. Também pode ser chamado de Stock Location ou Bin.

`Stock Location`: sinônimo operacional de Warehouse Location.

`Bin`: endereço físico curto usado na operação do depósito.

`Receiving Document`: documento de recebimento que registra chegada planejada ou iniciada de mercadorias sem atualizar saldo.

`Receiving Item`: item de um documento de recebimento com quantidade pedida, recebida, avariada e pendente.

`Goods Receipt`: confirmação física do recebimento, responsável por gerar movimento de estoque e saldo pendente de armazenagem.

`Put Away`: confirmação de armazenagem física da mercadoria recebida em uma localização final.

`Putaway Pending Quantity`: quantidade recebida fisicamente, mas ainda não armazenada na localização final e, portanto, não disponível.

`Origin Module`: origem funcional de uma movimentação de estoque, como `PURCHASE`, `POS`, `RESTAURANT_PRODUCTION`, `TRANSFER`, `LOSS` ou `INVENTORY_COUNT`.

`Business Process`: processo operacional da movimentação, como `RECEIVING`, `PUTAWAY`, `PRODUCTION`, `SALE`, `DELIVERY`, `RETURN`, `TRANSFER` ou `COUNT`.

`Inventory Balance`: saldo agregado por produto, filial, warehouse e location.

`Inventory Movement`: mudança operacional de saldo.

`Inventory Reservation`: bloqueio lógico de saldo disponível.

`Inventory Adjustment`: ajuste manual ou técnico de saldo.

`Inventory Count`: inventário ou contagem física.

`Inventory Transfer`: transferência entre warehouses, locations ou filiais.

`Recipe Engine`: engine futura de receitas do restaurante, separada do Inventory Engine.

`Daily Production`: planejamento e execução futura de produção diária do restaurante.

`Restaurant Production`: domínio futuro responsável por receitas, produção, consumo de insumos, desperdício, forecast e insights de IA.

`Inventory Transaction`: visão de consulta imutável de um `Inventory Movement`, usada como livro-razão operacional para reconstrução e auditoria de saldo. Não é uma segunda entidade de escrita.

## Restaurant

`KDS`: Kitchen Display System, painel operacional da cozinha.

`QR Code Menu`: cardápio acessado pelo cliente via QR Code.

`Table`: mesa operacional do restaurante.

`Sector`: área do restaurante, como salão, varanda ou área VIP.

`Waiter`: usuário ou papel operacional responsável por atendimento.

`Menu do Dia`: publicação comercial temporária de pratos disponíveis por filial, período e canal.

`Quantidade Vendável`: cota comercial diária de um item do cardápio; não é saldo físico de estoque.

`Recipe Engine`: engine futura para ficha técnica de pratos e consumo planejado de insumos.

`Daily Production`: produção diária futura de porções/pratos, separada do saldo bruto de insumos.

`Restaurant Operations Core`: domínio configurável por filial que reúne operação de restaurante, bar, lanchonete, café, pizzaria, food truck e delivery.

`Restaurant Operation`: configuração operacional de um segmento de alimentação em uma filial, incluindo modalidades de atendimento, ambientes, estações e canais.

`Order Entered By`: usuário que registrou um pedido.

`Table Responsible Waiter`: garçom responsável pela mesa, que pode ser diferente de quem registrou o pedido.

`Kitchen Station`: destino configurável de preparo, como cozinha, bar ou expedição.

`Table Account`: consolidação futura de itens e valores associados a uma mesa antes do fechamento no PDV.

## Sales, Fiscal E Finance

`POS`: ponto de venda.

`NFC-e`: Nota Fiscal de Consumidor Eletrônica.

`Cashier`: caixa operacional.

`Order`: pedido operacional.

`Sale`: venda concluída.

`Reservation`: reserva de produto ou estoque, conforme contexto.

## Demo

`Demo Environment`: ambiente oficial de demonstração e homologação.

`Scenario Engine`: mecanismo planejado para montar cenários operacionais.

`Demo Account`: conta criada para testes e demonstrações.

## Documentation

`Product Map`: mapa vivo do produto, com modulos implementados, em desenvolvimento, planejados e futuros.

`Knowledge Architecture`: organizacao oficial do conhecimento do ERP entre documentacao tecnica, Academy, Help Center, tutoriais, FAQ, materiais comerciais e AI/MCP.

`Help Center`: central futura de ajuda para usuarios finais, administradores, suporte, parceiros e implantadores.

`Tutorial`: guia passo a passo orientado a uma tarefa de usuario.

`FAQ`: perguntas frequentes sobre uso, configuracao, erros comuns ou comportamento esperado.

`Docs-as-Product`: principio de tratar documentacao como parte do produto entregue.

`Feature Documentation Standard`: padrao minimo para documentar uma funcionalidade nova.

## AI

`MCP`: Model Context Protocol, integração futura para ferramentas e agentes externos.

`AI Event`: evento derivado do ERP para análise futura por IA.

`Insight`: recomendação ou análise gerada por agente, sem efeito transacional automático.

`AI Gateway`: camada futura para controlar acesso de agentes, modelos e ferramentas ao contexto do ERP.

`Domain Tool`: ferramenta MCP futura especializada em um dominio, como Finance, Inventory, Restaurant, Production, HR ou Commercial.

`Marketing AI`: conjunto futuro de agentes para conteudo, campanhas, social media, copywriting, analytics e briefs de design.
