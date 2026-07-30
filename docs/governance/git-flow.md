# Git Flow Oficial

Este documento registra o fluxo Git obrigatório da Rigaud Tech Platform ERP.

## Repositório

```text
https://github.com/rigauddev/rigaud_tech_platform_erp.git
```

## Branches Permanentes

`main` representa código validado, estável e apto para produção.

`develop` representa integração das tasks concluídas e revisadas.

Não realizar desenvolvimento diretamente nessas branches.

## Branches de Trabalho

Usar nomes em minúsculas e separados por hífen:

```text
feature/<task-id>-<descricao>
fix/<task-id>-<descricao>
docs/<task-id>-<descricao>
hotfix/<descricao>
release/<versao>
```

## Fluxo de Task

```text
Atualizar develop
        ↓
Criar feature branch
        ↓
Implementar uma única Task
        ↓
Executar testes
        ↓
Atualizar documentação
        ↓
Atualizar task registry
        ↓
Commit
        ↓
Push
        ↓
Pull Request para develop
        ↓
Code Review
        ↓
Merge em develop
        ↓
Validação integrada
        ↓
Pull Request develop para main
        ↓
Merge em main após aprovação
```

## Início da Task

```bash
git status
git remote -v
git fetch origin
git checkout develop
git pull --ff-only origin develop
git checkout -b feature/<task-id>-<descricao>
```

Antes de iniciar, confirmar:

- working tree limpa;
- remoto correto;
- `develop` atualizada;
- branch criada a partir de `develop`;
- nenhuma alteração de outra task presente.

## Rastreabilidade

Cada task deve registrar:

- branch;
- commits;
- Pull Request para `develop`;
- merge commit em `develop`;
- Pull Request `develop → main`;
- merge commit em `main`;
- tag, quando houver;
- resultado dos testes;
- migration aplicada;
- documentação atualizada.
