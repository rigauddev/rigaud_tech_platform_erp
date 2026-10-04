# Changelog

## Unreleased

### Added

- RESTAURANT-004: Menu do Dia e disponibilidade comercial por produto, filial, data, período e canal, com migration `0025_menu_availability`, auditoria, dados demo e tela operacional baseada no canvas aprovado.

- RESTAURANT-003: equipe operacional por filial, CRUD auditado, migration `0024_restaurant_staff`, dados demo e tela de garçons alinhada à referência visual aprovada.

- RESTAURANT-002: setores e ambientes por filial, CRUD auditado, migration `0023_restaurant_sectors`, dados demo e tela responsiva alinhada ao padrão visual aprovado.

- RESTAURANT-001: fundação de salões e mesas, API multi-tenant auditada, migration `0022_restaurant_tables` e mapa operacional responsivo.
- RESTAURANT-001: evolução de app do garçom, handoff de pagamento, KDS, impressão e previsão de preparo registrada nas tasks responsáveis.

- DOC-011: Restaurant Operations Core documenta o núcleo configurável de alimentação, papéis, experiências Flutter, fluxo comum de pedidos e limites entre menu, estoque, produção, PDV e financeiro.

- REST-013: transferências internas de estoque com solicitação, despacho, recebimento, auditoria e movimentos imutáveis de saída e entrada.
- REST-013: migration `0021_inventory_transfers` e correção idempotente da migration `0019_inventory_count`.

- UI-004: seletor de idioma Português/English no Login, carrossel informativo, recuperação de senha visual e navegação compartilhada.
- UI-004: rota `/login/forgot-password` criada sem simular o envio de recuperação enquanto o serviço backend não existir.

- UI-003: menu lateral passa a refletir o contexto de acesso, exibindo o papel técnico ativo e ocultando áreas de plataforma para usuários sem essa permissão; a rota de Ambiente demo também passa a exigir acesso de plataforma.
- UI-003: a logo selecionada para Login é registrada no manifesto Flutter e exibida sem recorte ou escala artificial.

- REST-012: Stock Adjustments recebe catálogo de motivos, vínculo de estorno, endpoint de reversão compensatória e migration `0020_stock_adjustments`.
- DOC-010: roadmap do Restaurante passa a incluir Menu do Dia, disponibilidade comercial diária, contexto da mesa, garçom responsável e roteamento para cozinha antes do cardápio online e KDS.

- REST-011: Inventory Count adiciona documentos de inventario fisico, itens, ciclo draft/in_progress/finished/cancelled, auditoria e migration `0019_inventory_count`.
- REST-011: divergencias de contagem passam a gerar `InventoryMovement` imutavel do tipo `count`, com origem `INVENTORY` e processo `COUNT`.

- UI-002: navegação lateral reorganizada por contexto de trabalho, com grupos de visão geral, cadastros, estoque, conta e segurança, administração e desenvolvimento.
- UI-002: Login passa a usar a marca oficial atual em variante PNG transparente, sem fundo branco, margem excedente ou escala artificial.
- UI-002: logo oficial de Login atualizada para `Rigaud_Tech_profile.PNG`, com variante transparente para remover o fundo branco sem alterar a marca.
- UI-002: adicionados `make restart-backend` e `make restart-frontend` para recarga direcionada dos serviços Docker.

### Changed

- Correção transversal: Transferências passa a incluir a coluna de auditoria ausente pela migration `0027_transfer_audit_fix`; o endpoint deixa de retornar erro ao consultar a lista.
- Correção transversal: shell fixa tema claro, elimina transições entre páginas e deixa áreas ainda não entregues sem rota, evitando seleção incorreta de Início, Financeiro, Relatórios e Visão geral do Restaurante.
- Restaurant Production fica registrada como capability opcional por empresa/filial; Menu do Dia continua disponível sem receita, insumos ou custo de produção.

- UI-004/RESTAURANT-003: seletor de idioma do Login passa a usar bandeiras BR/US e persiste a escolha localmente; shell e Garçons e equipe aderem ao catálogo PT/EN.
- UI-004: Login passa a consumir a variante transparente correta da marca fornecida, corrigindo a ausência da logo no card de acesso.
- UI-003: navegação lateral foi alinhada ao layout aprovado, com menu direto por contexto, Restaurante expandido durante a operação e perfil/MFA concentrados em Configurações.
- RESTAURANT-003: rota de Garçons e equipe foi revisada para evitar restrições de layout no shell e manter abertura confiável pelo submenu contextual.

- UI-002: Splash passa a encaminhar automaticamente para Login, removendo o botão manual de continuar.
- UI-002: detalhes, edições e cadastros passam a apresentar ação de voltar para a rota-pai.
- UI-002: Ambiente demo é identificado como ferramenta de desenvolvimento e separado do menu operacional.
- UI-002: cards de Login reduzidos e formulário compactado para eliminar espaço vertical ocioso.

- REST-010: Inventory Transactions expõe `InventoryMovement` como livro razão imutável com filtros por produto, depósito, localização, tipo, origem, processo e módulo de origem.
- REST-010: endpoints `GET /api/v1/inventory/transactions` e `GET /api/v1/inventory/transactions/{transaction_id}` adicionados ao Inventory Engine.
- REST-010: Flutter Inventory passa a consultar transações de estoque com filtros por processo operacional.
- REST-010: documentação em `docs/inventory/transactions.md` e Academy de Inventory Transactions.
- REST-009: Put Away com `PutAwayService`, endpoint `POST /api/v1/inventory/putaway`, movimento `putaway`, liberação de saldo por localização e status documental `available`.
- REST-009: `InventoryMovement` passa a registrar `origin_module` e `business_process`, preparando auditoria, relatórios, Kafka, MCP e Restaurant Production futura.
- REST-009: Flutter Inventory recebe aba Put Away para confirmação por documento, produto, localização e quantidade, além de histórico de armazenagens.
- REST-009: documentação em `docs/inventory/putaway.md`, `docs/warehouse/putaway.md` e Academy de Put Away.
- DOC-009: arquitetura de documentação do produto, Central de Ajuda e conhecimento criada em `docs/index.md` e `docs/help/*`.
- DOC-009: mapa planejado do produto criado em `docs/architecture/product-map.md`, separando itens implementados, em desenvolvimento, planejados e futuros.
- DOC-009: padrao oficial de documentação por funcionalidade definido em `docs/help/feature-documentation-standard.md`.
- DOC-009: documentação futura de parceiros, revendedores, AI/MCP e Marketing AI registrada sem implementar funcionalidades.
- DOC-009: Academy, MkDocs, README, backlog, roadmap, task registry, decisões e glossário atualizados para Docs-as-Product.
- DOC-008: arquitetura oficial de distribuicao criada para Cloud, Cloud Dedicated, On-Premise e Hybrid.
- DOC-008: separacao entre Tenant e Deployment congelada, preservando `tenant_id = companies.id`.
- DOC-008: estrategia de operacao offline em tres niveis, Sync Gateway futuro e AI Gateway/MCP documentados.
- DOC-008: mapa funcional oficial documentado com Commercial, Inventory, Restaurant, Production, Financial, HR, Reports e AI/MCP.
- DOC-008: ADR `0008-deployment-distribution-architecture`, Academy e documentacao em `docs/architecture/*`.
- REST-008: Goods Receipt com `GoodsReceiptService`, confirmação física de `ReceivingDocument`, movimento `receipt`, saldo físico e `putaway_pending_quantity`.
- REST-008: endpoint `POST /api/v1/receiving-documents/{document_id}/confirm-receipt`, auditoria `goods_receipt.confirmed` e evento interno `inventory.receipt.confirmed`.
- REST-008: Flutter Receiving Documents passa a confirmar recebimento físico, exibir diferenças e acompanhar status `putaway_pending`.
- REST-008: migration `0017_goods_receipt`, documentação em `docs/inventory/goods-receipt.md`, `docs/warehouse/goods-receipt.md` e Academy de Goods Receipt.
- REST-008: fundação futura de IA/MCP criada em `erp-platform/backend/app/ai/` e documentação `docs/ai/overview.md`, sem implementar IA.
- REST-007: Receiving Documents com `ReceivingDocument`, `ReceivingItem`, CRUD, status documental, validação de quantidades, soft delete, auditoria, migration `0016_receiving_documents` e endpoints `/api/v1/receiving-documents`.
- REST-007: Flutter Receiving Documents com lista, cadastro, edição, detalhe, filtros e mudança de status.
- REST-007: Demo Environment atualizado com documentos de recebimento para restaurante e varejo.
- REST-007: documentação em `docs/inventory/receiving*.md`, `docs/warehouse/receiving.md` e Academy de Receiving Documents.
- REST-006: Warehouse Locations com CRUD de localizações físicas, filtros por depósito/zona/pesquisa, QR Code e código de barras preparados, ativação/inativação, ordenação, soft delete, auditoria, migration `0015_warehouse_locations` e endpoints `/api/v1/warehouse-locations`.
- REST-006: Flutter Warehouse Locations com lista, cadastro, edição, detalhe, filtros, status e ações operacionais.
- REST-006: Demo Environment atualizado com localizações físicas para restaurante e varejo.
- REST-006: documentação em `docs/warehouse/locations*.md` e Academy de Warehouse Locations.
- REST-005: Warehouse Zones com CRUD de zonas, tipo operacional, flags de recebimento/expedição/armazenagem/produção/quarentena, ordenação, soft delete, auditoria, migration `0014_warehouse_zones` e endpoints `/api/v1/warehouse-zones`.
- REST-005: Flutter Warehouse Zones com lista, cadastro, edição, detalhe, ativação/desativação e reordenação.
- REST-005: Demo Environment atualizado com zonas operacionais para restaurante e varejo.
- REST-005: documentação em `docs/warehouse/zones*.md` e Academy de Warehouse Zones.
- REST-004: Warehouse Management com CRUD de depósitos, depósito padrão por filial, soft delete, auditoria, migration `0013_warehouses` e endpoints `/api/v1/warehouses`.
- REST-004: Flutter Warehouses com lista, cadastro, edição, detalhe, status e definição de depósito padrão.
- REST-004: Demo Environment atualizado com depósitos padrão e operacionais para restaurante e varejo.
- REST-004: documentação em `docs/warehouse/*` e Academy de Warehouse Management.
- REST-003: Inventory Engine com saldos, movimentos, ajustes, reservas, migration `0012_inventory_engine`, auditoria e endpoints `/api/v1/inventory/*`.
- REST-003: Flutter Inventory com consulta de saldos, movimentações, ajuste e reserva usando Riverpod, Repository Pattern e Dio.
- REST-003: documentação em `docs/inventory/api.md`, `docs/inventory/endpoints.md`, `docs/inventory/entities.md`, `docs/inventory/permissions.md`, `docs/inventory/validation.md` e Academy de implementação.
- UI-001: tela de login ganha background visual próprio inspirado na identidade Rigaud Tech e no contexto ERP.
- UI-001: rodapé de login passa a exibir versão, build, API e ambiente.
- UI-001: documentação criada em `docs/ui/login-screen.md` e Academy UI em `erp-blueprint/docs/academy/ui/001-login-experience.md`.
- DEV-012: alinhamento de autenticação e tenant com login por email/senha, resolução backend de empresa, filial ativa e papel.
- DEV-012: migration `0011_auth_tenant_alignment` adiciona filial ativa, papel, permissões, histórico de troca de filial e lotação de trabalho.
- DEV-012: documentação de arquitetura em `docs/authentication/tenant-alignment.md` e Academy de alinhamento Auth/Tenant.
- DOC-006: criados `AI_DEVELOPMENT_CHARTER.md`, `ERP_DECISIONS.md` e `ERP_GLOSSARY.md` como base permanente para desenvolvimento com IA.
- DOC-006: `AGENTS.md`, `erp-blueprint/AGENTS.md` e `MASTER_DEVELOPMENT_PROMPT.md` passam a exigir leitura dos novos documentos.
- DOC-006: Academy de AI Development Charter criada em `erp-blueprint/docs/academy/engineering/002-ai-development-charter.md`.
- DOC-006: corrigido carregamento da logo na tela de login Flutter usando o asset registrado em `assets/images/logo_rigaud_tech.png`.
- DOC-005: domínio do Inventory Engine congelado em `docs/inventory/*` antes da implementação REST-003.
- DOC-005: ADR `0007-engine-first-development-strategy` oficializa o fluxo DOC → Implementação → Review → Integração para engines.
- DOC-005: Academy `erp-blueprint/docs/academy/inventory/001-inventory-engine-domain.md` criada para explicar estoque como engine compartilhada.
- DOC-003: Demo Environment com comandos `make demo`, `make demo-platform`, `make demo-restaurant`, `make demo-retail` e `make demo-reset`.
- DOC-003: seed idempotente para plataforma, Restaurante Sabor da Serra, Moda Center, filiais, usuários, memberships, categorias e 130 produtos demo.
- DOC-003: `make test` passa a limpar tenants demo operacionais antes do pytest para evitar conflito entre dados persistentes e fixtures de integração.
- DOC-003: documentação em `docs/demo/*` e aula Academy `erp-blueprint/docs/academy/demo/001-demo-environment.md`.
- DOC-003: evoluída para Demo Environment & Scenario Engine com API DEV-only `/api/v1/demo/*`, Dashboard Demo Flutter, scripts em `scripts/demo*.py`, comandos `make demo-scenarios`, `make playground` e senha demo `123456`.
- REST-002: módulo Categories com CRUD multi-tenant, hierarquia por `parent_id`, slug/código interno únicos, soft delete, ativação, desativação e ordenação manual.
- REST-002: endpoints `/api/v1/categories`, migration `0010_product_categories`, auditoria de categorias e mensagens centralizadas.
- REST-002: feature Flutter Categories com lista hierárquica, cadastro, edição, detalhe e ações de ativar/desativar/remover.
- REST-002: documentação em `docs/categories/*`, Academy de Categorias e registro inicial de Form Blueprint.
- DOC-002: prompt mestre de desenvolvimento criado em `erp-blueprint/MASTER_DEVELOPMENT_PROMPT.md`, consolidando arquitetura, Git Flow, testes, documentação, auditoria, SaaS, multitenancy, feature flags, roadmap e convenções.
- DOC-002: diretriz de Form Blueprint registrada para cadastros reutilizáveis por segmento a partir de REST-002.
- DEV-001: infraestrutura Docker de desenvolvimento com Backend, PostgreSQL 16, Redis, Mailpit, PgAdmin, Flutter Web e Nginx.
- DEV-001: Dockerfiles centralizados em `docker/backend/Dockerfile` e `docker/flutter/Dockerfile`.
- DEV-001: comandos `make` para subir, parar, reiniciar, acessar logs, subir backend/frontend, shells, lint, formatacao e testes.
- DEV-001: healthchecks, network compartilhada e volumes persistentes incluindo volume reservado para backups do PostgreSQL.
- DEV-001: documentação em `docs/development/docker.md`.
- DEV-002: backend starter com FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, JWT, DDD simplificado, Repository Pattern e Use Case Pattern.
- DEV-002: configuracao de Swagger, OpenAPI, health check, logs estruturados, ambientes e tratamento global de excecoes.
- DEV-002: documentação em `docs/backend/backend-starter.md`.
- DEV-002: estrutura modular independente para auth, companies, users, products, restaurant, fashion, inventory, sales, finance, delivery e fiscal.
- DEV-002: pacotes base de database, middlewares, exceptions, security, utils, requirements e teste inicial de `GET /health`.
- DEV-002: documentação de estrutura em `docs/backend/project-structure.md`.
- DEV-003: Flutter starter multiplataforma com MVVM, Riverpod, GoRouter, Dio, Freezed e Responsive Framework.
- DEV-003: temas claro e escuro, splash e tela de login vazia.
- DEV-003: documentação em `docs/frontend/flutter-starter.md`.
- DEV-003: configuração por ambiente, router centralizado, Dio preparado, storage local/seguro e design system compartilhado.
- DEV-003: telas iniciais de Splash, Login visual, Dashboard placeholder e 404.
- DEV-003: estrutura Feature First para auth, dashboard, companies, users, products, inventory, restaurant, fashion, sales, finance, delivery e fiscal.
- DEV-003: documentação em `docs/frontend/project-structure.md`, `docs/frontend/platforms.md`, `docs/frontend/responsive-design.md` e aula `erp-blueprint/docs/academy/flutter/001-flutter-multiplataforma.md`.
- REVIEW DEV-003: documentação atualizada com comandos de teste por plataforma e validação Web.
- DEV-004: fundação técnica de banco com SQLAlchemy async, sessão, naming convention, mixins, tipos compartilhados, tenant context e repositório base.
- DEV-004: Alembic assíncrono com migration técnica inicial `0001_database_core`.
- DEV-004: health check de banco em `/health/database` e `/api/v1/health/database`.
- DEV-004: testes unitários e de integração para database core.
- DEV-004: documentação em `docs/backend/database-core.md` e aula `erp-blueprint/docs/academy/backend/001-database-core.md`.
- DEV-004: documentação operacional de banco em `docs/database/*`, ADR `0001-database-tenancy-strategy` e aula `academy/postgresql/001-fundamentos-do-banco-do-erp.md`.
- DEV-005: fundação de autenticação multi-tenant com login, JWT access token, refresh token opaco rotacionável, logout e `/api/v1/auth/me`.
- DEV-005: tabelas técnicas `auth_users` e `auth_sessions` com migrations `0002_authentication` e `0003_auth_tenant_slug_email`.
- DEV-005: camada Auth organizada em Domain, Application, Infrastructure e Presentation, com Repository Pattern, Use Case Pattern e dependencies FastAPI.
- DEV-005: integração Flutter com AuthRepository, datasource remoto, controller Riverpod, storage seguro, Bearer interceptor, refresh automático, logout e dashboard protegido.
- DEV-005: testes unitários e de integração para autenticação, refresh rotation, revogação, tenant isolation e hash de refresh token.
- DEV-005: documentação em `docs/authentication/*`, ADR `0002-authentication-strategy` e aula `academy/security/001-autenticacao-multitenant-jwt.md`.
- ALINHAMENTO: plano oficial congelado do projeto em `erp-blueprint/docs/project-plan.md`.
- ALINHAMENTO: backlog e roadmap oficiais em `erp-blueprint/docs/backlog/master-backlog.md` e `erp-blueprint/docs/roadmap/master-roadmap.md`.
- ALINHAMENTO: regras permanentes de agentes em `AGENTS.md` e `erp-blueprint/AGENTS.md`.
- ALINHAMENTO: visão de produto e fluxo obrigatório de desenvolvimento em `erp-blueprint/docs/architecture/`.
- DEV-006: módulo Empresas com `Company` como raiz do tenant, CNPJ normalizado, slug/código únicos e status `active`, `inactive`, `suspended`.
- DEV-006: endpoints `/api/v1/companies`, `/api/v1/companies/current` e ações de ativar, desativar e suspender.
- DEV-006: autenticação atualizada para resolver tenant pela tabela `companies` e bloquear login de empresa inativa ou suspensa.
- DEV-006: Flutter Companies com lista, cadastro, edição, detalhes e rota de empresa atual.
- DEV-006: migration `0004_companies`, testes backend/Flutter e documentação `docs/companies/*`.
- DEV-007: módulo Usuários implementado sobre `auth_users`, preservando a identidade autenticável existente.
- DEV-007: `auth_users` evoluído com perfil, status `active/inactive/blocked`, auditoria básica, troca obrigatória de senha, tentativas de login e bloqueio técnico.
- DEV-007: endpoints `/api/v1/users`, `/api/v1/users/me`, ações de ativar, desativar, bloquear, desbloquear, trocar senha própria e resetar senha administrativo.
- DEV-007: autenticação integrada ao status do usuário, rastreio de tentativas inválidas, atualização de `last_login_at` e revogação de sessões por usuário.
- DEV-007: Flutter Users com lista, criação, edição, detalhe, perfil atual, troca de senha e reset administrativo.
- DEV-007: migration `0005_users`, testes backend/Flutter, ADR `0004-user-company-tenant` e documentação `docs/users/*`.
- DEV-008: governança transversal com `request_id`, `correlation_id`, logs estruturados, sanitização e catálogo central de mensagens.
- DEV-008: contrato padronizado de respostas da API com `success`, `code`, `message`, `data`, `meta`, `request_id` e `timestamp`.
- DEV-008: módulo Audit com tabela `audit_events`, migration `0006_audit_governance`, listagem e detalhe para superusuários.
- DEV-008: eventos de auditoria integrados a Authentication, Companies e Users.
- DEV-008: Flutter preparado para envelope padrão, erros com `request_id` e central administrativa de auditoria.
- DEV-008: task registry Docs-as-Code, templates oficiais de Task/Revisão e comando `make check-task TASK=DEV-008`.
- PLANEJAMENTO: DEV-009 registrada para autenticação em dois fatores habilitável/desabilitável por email, telefone e aplicativo autenticador.
- DEV-009: autenticação em dois fatores com TOTP, email OTP, SMS OTP, recovery codes e challenges temporários.
- DEV-009: segredos TOTP criptografados, OTP/recovery codes armazenados por hash e tokens emitidos somente após segundo fator quando MFA está ativo.
- DEV-009: endpoints `/api/v1/auth/mfa/*`, migration `0007_mfa_2fa`, mensagens centralizadas e auditoria de operações MFA.
- DEV-009: Flutter integrado ao fluxo `AUTH_MFA_REQUIRED`, verificação de código, configuração TOTP com QR Code e gestão de recovery codes.
- DEV-009: documentação em `docs/authentication/mfa-*.md`, docs locais do módulo Auth e aulas Academy de 2FA/TOTP/OTP.
- DOC-001: Git Flow oficial documentado com branches `main`/`develop`, branch por task, PR para `develop`, validação integrada e PR `develop → main`.
- DOC-001: templates de Pull Request, Issue de Task/Review, CONTRIBUTING e workflow básico de compliance adicionados.
- REST-001: módulo Products iniciado com entidade multi-tenant, API, migration `0008_products`, Flutter e documentação base.
- REST-001: suporte a criação, consulta, listagem, filtros, paginação, atualização, ativação, desativação, disponibilidade, soft delete, imagem principal, auditoria e mensagens da API.
- REVIEW REST-001: status funcional de Product separado da disponibilidade, códigos específicos de conflito/validação e testes monetários ampliados.
- REVIEW REST-001: validação Flutter em Android, iOS e macOS documentada, incluindo correção de xattrs no build nativo e limitação de CodeSign em workspace sincronizado.
- DEV-010: fundação de contexto ativo multi-tenant com `Company` como tenant raiz, filiais, memberships de empresa e memberships de filial.
- DEV-010: migration `0009_tenant_context` com `branches`, `company_memberships`, `branch_memberships` e contexto opcional em `auth_sessions`.
- DEV-010: endpoints `/api/v1/auth/context`, `/api/v1/auth/context/switch` e `/api/v1/companies/branches`.
- DEV-010: JWT preparado com `membership_id`, `branch_id`, `branch_membership_id`, `role` e `access_scope`.
- DEV-010: Flutter Auth preparado para ler opções de contexto e trocar contexto ativo sem implementar funcionalidades comerciais.
- DEV-010: documentação em `docs/authentication/context.md`, `docs/companies/*` e aula Academy de contexto ativo.
- REVIEW DEV-010: refresh e `/auth/me` passam a revalidar contexto ativo contra memberships e filiais no banco.
- REVIEW DEV-010: proteção explícita contra vínculo cruzado entre `CompanyMembership` e `Branch` de tenants diferentes.
- REVIEW DEV-010: testes ampliados para multiempresa, `all_branches`, membership inativo, refresh com contexto inválido e branch membership cross-tenant.

- REVIEW DEV-001: proxy Nginx resolve `backend` e `frontend` dinamicamente no DNS interno do Docker, evitando `502` após recriação dos containers.
- UI-001 Review: login passa a exibir carrossel informativo lateral em desktop com o mesmo design e tamanho do card de acesso, mantendo a tela sem scroll.
- UI-001 Review: renderização da logo no card de login ajustada para exibir a área útil do asset `assets/images/logo_rigaud_tech.png`.
- UI-001: tela de login remove scroll externo, centraliza card responsivo e ajusta renderização horizontal da logo.
- DEV-012: tela de login Flutter remove o campo Tenant e envia somente email e senha.
- DEV-012: endpoint `/api/v1/auth/login` deixa de aceitar tenant no payload.
- DEV-012: troca de contexto passa a negar usuário comum e manter tenant único por usuário.
- REVIEW DEV-001: removidas configuracoes Docker duplicadas, ajustado healthcheck do frontend, habilitada persistencia AOF no Redis, revisado proxy `/api` e removida variavel legada `FLUTTER_WEB_PORT`.
- REVIEW DEV-001: `make up`, `make backend` e `make flutter` agora executam preflight de Docker, Compose e espaco livre antes do build.
- REVIEW DEV-001: Dockerfile Flutter ajustado para executar como usuario `ubuntu` e evitar preparacao do Flutter toolchain como root durante o build.
- REVIEW DEV-001: `make up` ajustado para aguardar healthchecks com `--wait` e corrigir `safe.directory` do Flutter SDK.
- REVIEW DEV-001: permissões do Flutter SDK ajustadas no Dockerfile para permitir hot reload com usuário não-root.
- REVIEW DEV-001: imagem Flutter fixada em `ghcr.io/cirruslabs/flutter:3.41.9` para estabilizar o `make up`.
- REVIEW DEV-001: startup do Flutter ajustado para corrigir permissões do volume `flutter_pub_cache` antes de executar como `ubuntu`.
- REVIEW DEV-001: comando Flutter no container ajustado para usar caminho absoluto do SDK.
- REVIEW DEV-001: healthcheck do Nginx ajustado para rota interna `/nginx-health`, estabilizando o `make up --wait`.
- REVIEW DEV-003: removida duplicação residual da antiga feature `login` e estabilizados testes de navegação.
- REVIEW DEV-003: feature técnica `splash` alinhada ao padrão `data`, `domain` e `presentation`.
- DEV-004: engine assíncrona refinada com pool recycle, descarte via lifespan, sessão com rollback em erro e context manager externo.
- DEV-004: adicionados Unit of Work async, métodos de soft delete/restore, tenant obrigatório controlado e comandos Makefile para Alembic.
- DEV-004: migration inicial ajustada para criar apenas extensão PostgreSQL necessária, sem tabela artificial.
- DEV-005: módulo Auth deixou de ser apenas estrutura reservada e passou a conter a fundação técnica de autenticação.
- DEV-007: `is_active` passa a ser campo de compatibilidade derivado do `status` funcional do usuário.
- DEV-008: respostas de Auth, Companies e Users passam a incluir envelope padronizado e mantêm campos de compatibilidade no topo durante transição.
- DEV-009: login Auth passa a retornar `AUTH_MFA_REQUIRED` para usuários com MFA ativo, preservando o fluxo sem MFA para usuários existentes.
- REST-001: menu e rotas Flutter passam a incluir Products como primeira feature comercial do MVP Restaurante.
- REST-001: comandos `make lint`, `make format` e `make test` passam a configurar `safe.directory` para o SDK Flutter em containers temporários.
- DEV-010: criação de usuários passa a garantir membership padrão de empresa e filial quando existe filial matriz ativa.
- REVIEW DEV-010: memberships de empresa e filial passam a carregar campos de auditoria básica.
