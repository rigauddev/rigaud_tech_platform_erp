# AGENTS

Regras permanentes para qualquer agente ou sessão do Codex na Rigaud Tech Platform ERP.

## Fonte Oficial

Antes de executar qualquer Task, leia:

- `erp-blueprint/MASTER_DEVELOPMENT_PROMPT.md`
- `AI_DEVELOPMENT_CHARTER.md`
- `ERP_DECISIONS.md`
- `ERP_GLOSSARY.md`
- `erp-blueprint/docs/project-plan.md`
- `erp-blueprint/docs/architecture/product-vision.md`
- `erp-blueprint/docs/architecture/development-workflow.md`
- `docs/governance/git-flow.md`
- `erp-blueprint/docs/backlog/master-backlog.md`
- `erp-blueprint/docs/roadmap/master-roadmap.md`
- ADRs em `erp-blueprint/docs/adr/`
- documentação do módulo afetado

A ausência de contexto não autoriza o agente a inventar uma nova arquitetura.

A implementação existente tem prioridade sobre suposições, desde que não contradiga um ADR aprovado.

## Regras de Execução

- Identificar a Task atual antes de alterar arquivos.
- Executar uma Task por prompt.
- Não avançar automaticamente para a próxima Task.
- Não alterar arquitetura por iniciativa própria.
- Não reordenar backlog.
- Não recriar estruturas existentes.
- Não criar arquitetura paralela.
- Não substituir tecnologias definidas sem ADR futuro.
- Não implementar funcionalidades futuras.
- Não misturar múltiplas Tasks.
- Não desenvolver diretamente em `main` ou `develop`.
- Registrar rastreabilidade Git no task registry quando a task gerar branch, commits, PRs, merges ou tag.
- Não colocar regras de negócio em routers.
- Não acessar banco diretamente em endpoints.
- Atualizar testes, documentação, Academy e `CHANGELOG.md`.
- Executar validações da Task.
- Apresentar relatório final e parar.
- Conferir `ERP_DECISIONS.md` antes de rediscutir decisões de negócio já congeladas.
- Usar `ERP_GLOSSARY.md` para nomes oficiais do domínio.
- Obedecer a DEV-012: login por email/senha, empresa única por usuário e filial ativa única.

## Quando Houver Dúvida

1. Consultar ADRs.
2. Consultar o Blueprint.
3. Preservar a arquitetura existente.
4. Documentar a dúvida.
5. Parar se a decisão puder quebrar o plano oficial.
