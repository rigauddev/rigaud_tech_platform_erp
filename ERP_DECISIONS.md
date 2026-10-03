# ERP Decisions

Decisões de produto, domínio e arquitetura que não devem ser rediscutidas sem ADR ou task específica.

## Produto E Plataforma

- O nome oficial é `Rigaud Tech Platform ERP`.
- A plataforma é modular, multi-tenant e multiplataforma.
- O Core deve ser reutilizado por Restaurante, Loja e futuros segmentos.
- Engines compartilhadas devem atender múltiplos segmentos.

## Tenant E Filial

- `Company` é a raiz oficial do tenant.
- `tenant_id = companies.id`.
- Tenant e deployment sao conceitos diferentes.
- Tipos oficiais de deployment: `CLOUD_SHARED`, `CLOUD_DEDICATED`, `ON_PREMISE` e `HYBRID`.
- Um tenant pode migrar entre deployments sem criar nova empresa.
- O `tenant_id` deve permanecer estavel durante migracoes sempre que tecnicamente possivel.
- `Branch` representa filial operacional dentro de um tenant.
- DEC-001: um usuário pertence a exatamente uma empresa/tenant.
- DEC-002: um usuário possui exatamente uma filial ativa.
- DEC-003: troca de filial só pode ser feita por gestor, administrador ou permissão explícita.
- DEC-004: `tenant_id` permanece obrigatório em tabelas SaaS e On-Premise.
- O frontend nunca define `tenant_id` confiável.
- O backend resolve tenant e filial pelo usuário autenticado e contexto ativo.
- Usuario comum nao escolhe empresa no login.

## Deployment E Distribuicao

- Cloud inicial usa modelo SaaS multi-tenant compartilhado.
- `CLOUD_DEDICATED` fica reservado para isolamento operacional ou contrato especial.
- On-Premise e o mesmo produto executando no ambiente local do cliente.
- Servidor de producao recomendado para On-Premise e Linux.
- Windows, macOS, Linux, Android e iOS sao plataformas de acesso; nao definem o servidor recomendado.
- Hybrid prepara servidor local com Sync Gateway futuro para Rigaud Cloud.
- Nem todos os dados precisam ser enviados para a nuvem em deployments Hybrid.
- Partner/Reseller nao e tenant.
- Inadimplencia ou suspensao nunca apaga dados automaticamente.
- Suspensao bloqueia acesso conforme politica comercial, preservando dados.

## Produtos E Estoque

- Produto não possui saldo.
- Saldo pertence ao Inventory Engine.
- Estoque é controlado por tenant, filial, warehouse e location quando aplicável.
- Warehouse Zone é a camada operacional entre Warehouse e Stock Location.
- Warehouse Location é o endereço físico ou bin dentro de uma Warehouse Zone.
- Receiving Document registra chegada e conferência documental, sem movimentar estoque.
- Goods Receipt confirma recebimento físico por `InventoryMovement` do tipo `receipt`.
- Mercadoria recebida fica em `putaway_pending_quantity` até o Put Away liberar disponibilidade.
- Put Away confirma armazenagem por `InventoryMovement` do tipo `putaway`.
- `InventoryMovement` deve registrar `origin_module` e `business_process` para rastreabilidade de origem e processo.
- Reserva não altera saldo físico.
- `InventoryBalance` nunca deve ser alterado diretamente por funcionalidades de negócio.
- Toda alteração de saldo deve ocorrer por `InventoryMovement`, mantendo `InventoryBalance` como projeção auditável.
- `Inventory Transaction` é a visão de consulta imutável de um `InventoryMovement`, usada como livro-razão operacional; não cria uma segunda fonte de verdade.
- Transferências internas usam documento no mesmo tenant: `transfer_out` só ocorre no despacho e `transfer_in` só ocorre no recebimento. Solicitar não altera saldo; recebimento parcial e divergências seguem como evolução explícita do WMS.
- Tipos planejados de movimento: `RECEIPT`, `SALE`, `TRANSFER`, `ADJUSTMENT`, `RESERVATION`, `RELEASE`, `RETURN`, `LOSS` e `CONSUMPTION`.
- Consumo automático de insumos do Restaurante será implementado em task futura do módulo Restaurant.
- Pratos não serão controlados diretamente pelo estoque. Restaurante usará EPIC futura `EPIC-RESTAURANT-PRODUCTION` com Recipe Engine, Production Planning, Daily Production, Kitchen Production, Consumption, Waste, Forecast e AI Insights.
- Produção futura consumirá insumos por `InventoryMovement`, usando `origin_module=RESTAURANT_PRODUCTION` e `business_process=PRODUCTION`.
- Menu do Dia é uma publicação comercial por filial, período e canal. A quantidade vendável diária não altera nem duplica `InventoryBalance`.
- Pedido originado pelo cardápio online deve portar o contexto da mesa, direcionar notificação ao garçom responsável e ser roteado para a estação/impressora de cozinha configurada.
- Movimento confirmado não é editado.
- Correção de estoque deve gerar novo movimento ou ajuste.
- Ajustes de estoque possuem motivo padronizado e texto descritivo obrigatório. Estornos são compensatórios e vinculados ao ajuste original; o lançamento original permanece imutável.
- Toda nova entidade operacional deve possuir UUID interno, código curto quando fizer sentido, e ser avaliada para QR Code, código de barras, auditoria completa, sincronização offline, eventos Kafka, operação multi-filial e compatibilidade SaaS/On-Premise, sem antecipar implementação fora da task vigente.

## Restaurant Operations

- Restaurant, Bar, Lanchonete, Café, Pizzaria, Food Truck e Delivery compartilham um Restaurant Operations Core configurável por filial; não serão módulos paralelos.
- Gestão, Garçom, KDS, PDV e Cliente/Menu Online são experiências sobre o mesmo backend, eventos e base Flutter.
- Pedido deve separar `order_entered_by` de `table_responsible_waiter` e preservar ambos na auditoria.
- KDS e impressão serão consumidores do mesmo roteamento por estação; não haverá fluxos concorrentes de preparo.
- Disponibilidade comercial diária continua separada de `InventoryBalance` e de Restaurant Production.
- Receita, produção, consumo, desperdício, custos e forecast continuam restritos à EPIC-RESTAURANT-PRODUCTION.

## Segurança E Acesso

- Login usa email e senha. O tenant é resolvido pelo backend a partir do usuário.
- JWT é curto e controlado pelo backend.
- JWT deve carregar `user_id`, `tenant_id`, `branch_id` e `role`.
- Refresh token é opaco, rotacionável e persistido apenas como hash.
- MFA pode ser habilitado ou desabilitado por usuário.
- Canais MFA preparados: email, telefone e aplicativo TOTP.
- Superusuários administrativos devem ser validados explicitamente.

## API, Auditoria E Observabilidade

- Toda API usa envelope padronizado.
- Mensagens e códigos ficam no catálogo central.
- Eventos críticos devem ser auditados.
- `request_id` acompanha resposta e logs.
- Dados sensíveis não devem aparecer em logs.

## SaaS E Feature Flags

- SaaS fica desacoplado dos módulos comerciais.
- Planos, assinaturas, entitlements e billing não devem vazar para regra de negócio segmentada.
- Bloqueios comerciais passam por entitlements e feature flags.
- Billing real entra por Strategy Pattern em task específica.

## Demo Environment

- Tudo que for desenvolvido deve ser demonstrável.
- Módulos funcionais devem incluir dados demo ou registrar por que ainda não podem ser demonstrados.
- Cenários completos só devem materializar tabelas existentes.

## Documentacao E Conhecimento

- Documentacao e parte do produto, nao apenas suporte ao desenvolvimento.
- A entrada principal de produto fica em `docs/index.md`.
- O mapa vivo do produto fica em `docs/architecture/product-map.md`.
- Funcionalidades operacionais devem nascer com documentacao tecnica, Academy e, quando aplicavel, conteudo de Help Center.
- O Help Center futuro deve reutilizar conteudo versionado do repositorio.
- Conteudo de usuario final nao deve expor detalhes internos desnecessarios.
- Conteudo para parceiros e revendedores nao altera o modelo de tenant.
- Conteudo usado por AI/MCP deve respeitar tenant, filial, role, permissoes e auditoria.

## Offline Futuro

- Offline-first é planejado.
- SQLite local só entra em task futura.
- Operações offline devem considerar idempotência, fila, retry, conflitos e auditoria.

## IA E MCP Futuro

- IA não faz parte do MVP operacional inicial.
- A arquitetura deve reservar espaço para providers, agentes, prompts, ferramentas, MCP, memória, embeddings, RAG e eventos.
- A arquitetura futura podera usar AI Gateway -> MCP -> ferramentas especificas de dominio.
- MCPs futuros planejados: Finance, Inventory, Restaurant, Production, HR e Commercial.
- Todo MCP deve respeitar tenant, branch, role, permissions e audit.
- IA deve consumir eventos do ERP e permanecer desacoplada das regras transacionais.
- Insights futuros não devem alterar dados transacionais sem workflow explícito, auditoria e permissão.
