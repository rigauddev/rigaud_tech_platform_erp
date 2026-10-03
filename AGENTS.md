# AGENTS

Regras permanentes do workspace Rigaud Tech Platform ERP.

Leia primeiro:

- `erp-blueprint/MASTER_DEVELOPMENT_PROMPT.md`
- `erp-blueprint/AGENTS.md`
- `AI_DEVELOPMENT_CHARTER.md`
- `ERP_DECISIONS.md`
- `ERP_GLOSSARY.md`
- `CONTRIBUTING.md`
- `docs/governance/git-flow.md`
- `erp-blueprint/docs/project-plan.md`
- `erp-blueprint/docs/backlog/master-backlog.md`
- `erp-blueprint/docs/roadmap/master-roadmap.md`
- ADRs em `erp-blueprint/docs/adr/`

Regra principal:

```text
Uma Task
Um Prompt
Uma Entrega
```

Não alterar arquitetura, não reordenar backlog e não avançar automaticamente para a próxima Task.

Fluxo Git obrigatório:

- não desenvolver diretamente em `main` ou `develop`;
- usar branch por task;
- abrir PR da branch de trabalho para `develop`;
- validar `develop`;
- abrir PR `develop` para `main`;
- registrar branch, commits, PRs, merges e tag no task registry quando existirem.

Operação Docker obrigatória:

- antes de alterar, confirmar a branch, o upstream remoto, o roadmap e o backlog aplicáveis;
- após uma alteração, identificar se algum serviço em execução realmente precisa ser recarregado;
- quando necessário, reiniciar somente o serviço afetado com `docker compose restart <servico>` ou com os alvos específicos do Makefile;
- não criar uma segunda stack, não trocar o nome do projeto Compose e não recriar containers saudáveis sem necessidade;
- usar `docker compose up -d --build <servico>` somente quando Dockerfile, dependências ou configuração do Compose daquele serviço exigirem rebuild.

A ausência de contexto não autoriza o agente a inventar uma nova arquitetura.

A implementação existente tem prioridade sobre suposições, desde que não contradiga um ADR aprovado.

Antes de implementar, confirme as decisões permanentes em `ERP_DECISIONS.md` e a linguagem oficial em `ERP_GLOSSARY.md`.

Decisão congelada da DEV-012: login usa email e senha; usuário pertence a uma empresa e possui uma filial ativa única.

Decisão congelada da DOC-008: tenant e deployment sao conceitos diferentes. Tenant e `Company`; deployment pode ser `CLOUD_SHARED`, `CLOUD_DEDICATED`, `ON_PREMISE` ou `HYBRID`.

Decisão congelada da DOC-009: documentacao e parte do produto. Toda funcionalidade deve avaliar documentacao tecnica, Academy, Help Center, FAQ e tutorial, sem implementar telas ou agentes fora da task vigente.
