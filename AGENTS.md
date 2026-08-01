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

A ausência de contexto não autoriza o agente a inventar uma nova arquitetura.

A implementação existente tem prioridade sobre suposições, desde que não contradiga um ADR aprovado.

Antes de implementar, confirme as decisões permanentes em `ERP_DECISIONS.md` e a linguagem oficial em `ERP_GLOSSARY.md`.
