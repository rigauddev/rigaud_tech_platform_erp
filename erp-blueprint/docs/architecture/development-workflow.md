# Fluxo de Desenvolvimento

Toda funcionalidade deve seguir:

```text
Planejamento
    ↓
Task
    ↓
Implementação
    ↓
Testes
    ↓
Documentação
    ↓
Academy
    ↓
Revisão
    ↓
Merge
```

## Regra Principal

```text
Uma Task
Um Prompt
Uma Entrega
```

O Codex deve:

- Analisar o projeto existente.
- Ler `AGENTS.md`.
- Ler a Task.
- Ler documentação relacionada.
- Implementar somente a Task solicitada.
- Executar testes.
- Atualizar documentação.
- Atualizar `CHANGELOG.md`.
- Apresentar relatório.
- Parar.

## Entrega Obrigatória

Cada Task somente pode ser considerada concluída quando possuir:

- Código, quando aplicável.
- Testes.
- Documentação.
- `CHANGELOG.md`.
- Migrations, quando aplicável.
- Academy.
- Comandos de validação.
- Resultado dos testes.
- Mensagem de commit sugerida.

## Proibições Permanentes

O Codex não pode:

- Alterar arquitetura por iniciativa própria.
- Reordenar backlog.
- Antecipar Tasks.
- Implementar funcionalidades futuras.
- Recriar estruturas existentes.
- Criar arquitetura paralela.
- Substituir tecnologias definidas.
- Misturar múltiplas Tasks.
- Incluir regras de negócio em routers.
- Acessar banco diretamente em endpoints.
- Ignorar testes.
- Ignorar documentação.
- Ignorar migrations.
- Seguir automaticamente após concluir a Task.
