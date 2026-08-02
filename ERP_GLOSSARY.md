# ERP Glossary

Glossário oficial do domínio Rigaud Tech Platform ERP.

## Core

`Tenant`: limite lógico de dados de uma empresa. No projeto, é `Company`.

`Company`: empresa raiz do tenant.

`Branch`: filial operacional de uma empresa.

`Active Branch`: filial operacional única ativa do usuário autenticado.

`Membership`: vínculo legado/compatível usado para contexto e permissões até a consolidação de RBAC.

`Work Assignment`: lotação operacional de um usuário em uma filial, com início, fim e histórico.

`Branch History`: trilha de auditoria para mudanças de filial ativa.

`Active Context`: empresa, filial e papel ativos resolvidos pelo backend para a sessão autenticada.

`Feature Flag`: chave que habilita ou desabilita comportamento.

`Entitlement`: direito de uso derivado de plano, assinatura ou regra comercial.

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

`Stock Location`: local interno dentro de um warehouse.

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
