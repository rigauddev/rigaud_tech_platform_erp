# Master Development Prompt

Fonte operacional para qualquer agente, desenvolvedor ou sessão Codex da Rigaud Tech Platform ERP.

Este documento consolida a estratégia do projeto. Ele deve ser lido antes de qualquer Task, junto com `AGENTS.md`, `erp-blueprint/AGENTS.md`, ADRs, backlog, roadmap e documentação do módulo afetado.

## Identidade do Projeto

Nome oficial:

```text
Rigaud Tech Platform ERP
```

A plataforma é um ERP modular, multi-tenant e multiplataforma. O Core deve ser reutilizado por Restaurante, Loja de Roupas e futuros segmentos.

## Regra Principal

```text
Uma Task
Um Prompt
Uma Entrega
```

Cada execução deve identificar a Task atual, analisar a estrutura existente, usar a branch correta, implementar somente o escopo solicitado, atualizar testes e documentação, executar validações, apresentar relatório final e parar.

## Fontes Oficiais

Leitura obrigatória antes de alterar arquivos:

- `AGENTS.md`
- `erp-blueprint/AGENTS.md`
- `CONTRIBUTING.md`
- `docs/governance/git-flow.md`
- `erp-blueprint/docs/project-plan.md`
- `erp-blueprint/docs/architecture/product-vision.md`
- `erp-blueprint/docs/architecture/development-workflow.md`
- `erp-blueprint/docs/backlog/master-backlog.md`
- `erp-blueprint/docs/roadmap/master-roadmap.md`
- ADRs em `erp-blueprint/docs/adr/`
- documentação do módulo afetado em `docs/`
- documentação local do módulo em `erp-platform/backend/app/modules/<module>/README.md` ou `erp-platform/frontend/lib/features/<feature>/README.md`, quando existir.

## Stack Oficial

Backend:

- Python 3.13
- FastAPI
- SQLAlchemy 2.x assíncrono
- Alembic
- Pydantic v2
- PostgreSQL
- Redis
- JWT
- Pytest
- Docker

Frontend:

- Flutter
- Riverpod
- GoRouter
- Dio
- Freezed
- MVVM
- Feature First
- Android, iOS, Web, Windows, Linux e macOS

Infraestrutura:

- Docker Compose
- PostgreSQL 16
- Redis
- Mailpit
- PgAdmin
- Nginx

Nenhuma tecnologia oficial deve ser substituída sem ADR futura.

## Arquitetura

Backend:

- Clean Architecture
- DDD simplificado
- Repository Pattern
- Use Case Pattern
- Dependency Injection
- Async/Await
- routers sem regra de negócio;
- endpoints sem acesso direto ao banco.

Frontend:

- Feature First
- MVVM
- Riverpod para estado
- GoRouter para navegação
- Dio para HTTP
- tema claro e escuro
- responsividade por plataforma
- widgets sem regra de negócio.

Organização esperada para módulos backend:

```text
erp-platform/backend/app/modules/<module>/
  application/
  domain/
  infrastructure/
  presentation/
  tests/
  README.md
```

## Multi-Tenancy

O tenant oficial é `Company`.

Entidades tenant-aware devem usar:

```text
tenant_id = companies.id
```

Regras permanentes:

- o frontend nunca define `tenant_id` confiável;
- o backend resolve tenant pelo usuário autenticado e contexto ativo;
- filtros por tenant são obrigatórios em repositórios e use cases;
- não misturar dados entre empresas;
- filiais devem pertencer ao tenant ativo;
- instalações SaaS usam API central e PostgreSQL compartilhado;
- instalações on-premises usam um único PostgreSQL local por empresa.

## SaaS, Planos e Feature Flags

A plataforma deve manter SaaS desacoplado dos módulos de negócio.

Conceitos oficiais:

- Planos
- Assinaturas
- Entitlements
- Feature Flags
- Billing Providers

Regras:

- módulos comerciais não devem conhecer detalhes de billing provider;
- billing real deve entrar por Strategy Pattern;
- `FakeBillingProvider` é aceito para desenvolvimento;
- bloqueios comerciais devem passar por entitlements/feature flags;
- integrações reais de cobrança e webhooks pertencem a Tasks futuras específicas.

## Segurança

Padrões obrigatórios:

- JWT com claims controladas pelo backend;
- refresh token opaco e rotacionável;
- senhas sempre com hash;
- dados sensíveis nunca em logs;
- MFA habilitável/desabilitável por usuário;
- canais MFA preparados: email, telefone e aplicativo autenticador TOTP;
- RBAC preparado por roles, memberships e contexto ativo;
- validação de superusuário para endpoints administrativos.

## API, Logs e Auditoria

Toda API deve usar envelope padronizado:

```text
success
code
message
data
meta
request_id
timestamp
```

Regras:

- códigos e mensagens devem ficar no catálogo central;
- erros internos não devem vazar para o cliente;
- `request_id` deve acompanhar respostas e logs;
- `X-Correlation-ID` pode ser usado quando enviado pelo cliente;
- logs devem ser estruturados;
- auditoria persistida deve registrar eventos críticos;
- eventos de auditoria usam nomes estáveis como `category.created`.

## Banco de Dados

Regras permanentes:

- PostgreSQL compartilhado com isolamento lógico por `tenant_id`;
- UUID como identificador padrão;
- timestamps padronizados;
- soft delete quando aplicável;
- auditoria básica com `created_by`, `updated_by`, `deleted_by`;
- Alembic para migrations;
- migrations reversíveis;
- nenhuma tabela sem necessidade da Task;
- nenhuma entidade futura antecipada.

## Form Blueprint

A partir de REST-002, todo módulo com cadastro deve considerar um catálogo de formulários reutilizáveis.

Objetivo:

- acelerar implantação por segmento;
- permitir presets por ramo;
- reduzir configuração manual;
- manter cadastros compartilhados entre Restaurante, Loja e futuros segmentos.

Exemplos futuros:

- Restaurante: Bebidas, Pratos, Sobremesas.
- Loja: Camisetas, Calças, Tênis, Bolsas.
- Segmentos futuros: Farmácia, Oficina, Pet Shop.

Diretriz:

- documentar o blueprint do formulário quando um módulo de cadastro nascer;
- não implementar carregamento automático de presets sem Task específica;
- não misturar Form Blueprint com regra comercial do módulo.

## Backlog e Roadmap

Ordem oficial do MVP Restaurante:

1. REST-001 — Cadastro de Produtos
2. DEV-010 — Tenant, Memberships, Filiais e Contexto Ativo
3. DEV-011 — Assinaturas, Planos e Limites
4. REST-002 — Categorias
5. REST-003 — Controle de Estoque
6. REST-004 — Mesas
7. REST-005 — Setores
8. REST-006 — Garçons
9. REST-007 — QR Code das Mesas
10. REST-008 — Cardápio Online
11. REST-009 — Pedido pelo Cliente
12. REST-010 — Pedido pelo Garçom
13. REST-011 — Painel da Cozinha — KDS
14. REST-012 — Delivery
15. REST-013 — Caixa
16. REST-014 — Fechamento da Venda
17. REST-015 — Cupom ou NFC-e

Não reordenar o backlog. Não avançar automaticamente para a próxima Task.

## Git Flow

Não desenvolver diretamente em `main` ou `develop`.

Fluxo:

```text
develop
  -> feature/<task-id>-<descricao>
  -> commits pequenos
  -> push
  -> PR para develop
  -> validação integrada
  -> PR develop para main
  -> tag quando aplicável
```

Registrar no task registry:

- branch;
- commits;
- PR para develop;
- merge em develop;
- PR develop para main;
- merge em main;
- tag;
- testes executados;
- migrations;
- documentação.

## Testes e Validação

Validações padrão:

```bash
make lint
make test
make check-task TASK=<TASK-ID>
```

Backend:

```bash
docker compose --env-file .env.example exec -T backend ruff check app tests migrations
docker compose --env-file .env.example exec -T backend ruff format --check app tests migrations
docker compose --env-file .env.example exec -T backend pytest
```

Frontend:

```bash
cd erp-platform/frontend
flutter analyze
flutter test
flutter build web --dart-define=API_BASE_URL=http://localhost:8000
```

Plataformas:

- validar Android Emulator quando disponível;
- validar iOS Simulator somente em host macOS com Xcode configurado;
- validar macOS somente em host macOS;
- não executar builds Windows/Linux em host incompatível;
- registrar limitações reais no relatório final.

## Documentação

Cada Task deve atualizar, quando aplicável:

- `README.md`
- `CHANGELOG.md`
- `docs/<module>/`
- README local do módulo;
- Academy em `erp-blueprint/docs/academy/`;
- backlog;
- roadmap;
- task registry;
- OpenAPI, quando a API mudar.

## Proibições

Não fazer:

- funcionalidade fora da Task;
- CRUD futuro não solicitado;
- regra de negócio em widget ou router;
- acesso direto ao banco no endpoint;
- segredo em código ou documentação;
- URLs fixas sem configuração por ambiente;
- alteração de arquitetura sem ADR;
- reordenação de backlog;
- refatoração ampla sem necessidade;
- criação de arquitetura paralela;
- avanço automático para a próxima Task.

## Próxima Task Após Esta Diretriz

Depois deste documento estar versionado, a próxima feature planejada é:

```text
REST-002 — Categorias de Produtos
```

Ela deve iniciar em:

```text
feature/rest-002-product-categories
```

e deve continuar obedecendo a este Master Development Prompt.
