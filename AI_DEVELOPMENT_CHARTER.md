# AI Development Charter

Constituição operacional para desenvolvimento com IA na Rigaud Tech Platform ERP.

Este documento deve ser lido antes de qualquer task, junto com `AGENTS.md`, `erp-blueprint/MASTER_DEVELOPMENT_PROMPT.md`, `ERP_DECISIONS.md`, `ERP_GLOSSARY.md`, backlog, roadmap, ADRs e documentação do módulo afetado.

## Princípios Permanentes

- Documentação é parte da entrega.
- Nenhuma funcionalidade sem testes.
- Nenhuma funcionalidade crítica sem auditoria.
- Nenhuma funcionalidade comercial sem cenário de demonstração quando aplicável.
- Toda decisão de negócio recorrente deve ser registrada em `ERP_DECISIONS.md`.
- Toda linguagem de domínio recorrente deve ser registrada em `ERP_GLOSSARY.md`.
- Pesquisar documentação oficial antes de usar bibliotecas, APIs, padrões ou ferramentas novas.
- Não usar blogs como fonte primária quando existir documentação oficial.
- Não criar código duplicado.
- Preferir composição em vez de herança.
- Manter código pequeno, testável e alinhado ao padrão existente.
- Toda API deve seguir o envelope padrão.
- Toda funcionalidade deve respeitar multi-tenant, filial ativa única, auditoria e feature flags quando aplicável.
- Login sempre usa email e senha; tenant e filial são resolvidos pelo backend.
- Todo módulo novo deve ser demonstrável no Demo Environment quando houver superfície funcional.
- Toda funcionalidade Flutter deve nascer preparada para Web, Android, iOS, Windows, Linux e macOS, preservando uma única base de código.

## Fluxo Obrigatório

```text
Pesquisar documentação oficial quando necessário
    ↓
Ler AGENTS.md
    ↓
Ler erp-blueprint/MASTER_DEVELOPMENT_PROMPT.md
    ↓
Ler AI_DEVELOPMENT_CHARTER.md
    ↓
Ler ERP_DECISIONS.md
    ↓
Ler ERP_GLOSSARY.md
    ↓
Ler Task Registry
    ↓
Implementar somente a task
    ↓
Executar testes
    ↓
Atualizar documentação
    ↓
Atualizar Academy
    ↓
Atualizar CHANGELOG
    ↓
Atualizar Task Registry
    ↓
Publicar branch e abrir PR quando aplicável
    ↓
Parar
```

## Regra De Escopo

Uma Task, Um Prompt, Uma Entrega.

A ausência de contexto não autoriza criar arquitetura nova, antecipar módulo futuro ou alterar decisão já registrada.

## Regras Para Engines

Engines devem seguir:

```text
DOC
    ↓
IMPLEMENTAÇÃO
    ↓
REVIEW
    ↓
INTEGRAÇÃO
```

Nenhuma engine deve começar pela implementação quando o domínio ainda não estiver documentado.

## Regras Para Código

- Routers não possuem regra de negócio.
- Widgets não possuem regra de negócio.
- Repositórios filtram por tenant quando a entidade for tenant-aware.
- Use cases coordenam regras de aplicação.
- Domínio preserva invariantes.
- Testes cobrem sucesso, erro, isolamento multi-tenant e casos críticos.
- Logs não expõem dados sensíveis.

## Regras Para Documentação

Cada entrega deve atualizar:

- documentação operacional;
- Academy, quando houver aprendizado reutilizável;
- CHANGELOG;
- Task Registry;
- READMEs locais quando o módulo for afetado.
