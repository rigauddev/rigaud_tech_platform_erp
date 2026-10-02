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

`Goods Receipt`: confirmação física futura do recebimento, responsável por gerar movimento de estoque.

`Put Away`: endereçamento físico futuro da mercadoria recebida para uma localização.

`Putaway Pending Quantity`: quantidade recebida fisicamente, mas ainda não armazenada na localização final e, portanto, não disponível.

`Inventory Balance`: saldo agregado por produto, filial, warehouse e location.

`Inventory Movement`: mudança operacional de saldo.

`Inventory Reservation`: bloqueio lógico de saldo disponível.

`Inventory Adjustment`: ajuste manual ou técnico de saldo.

`Inventory Count`: inventário ou contagem física.

`Inventory Transfer`: transferência entre warehouses, locations ou filiais.

`Inventory Transaction`: registro técnico imutável para reconstrução e auditoria de saldo.

## Restaurant

`KDS`: Kitchen Display System, painel operacional da cozinha.

`QR Code Menu`: cardápio acessado pelo cliente via QR Code.

`Table`: mesa operacional do restaurante.

`Sector`: área do restaurante, como salão, varanda ou área VIP.

`Waiter`: usuário ou papel operacional responsável por atendimento.

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

## AI

`MCP`: Model Context Protocol, integração futura para ferramentas e agentes externos.

`AI Event`: evento derivado do ERP para análise futura por IA.

`Insight`: recomendação ou análise gerada por agente, sem efeito transacional automático.

`AI Gateway`: camada futura para controlar acesso de agentes, modelos e ferramentas ao contexto do ERP.

`Domain Tool`: ferramenta MCP futura especializada em um dominio, como Finance, Inventory, Restaurant, Production, HR ou Commercial.
