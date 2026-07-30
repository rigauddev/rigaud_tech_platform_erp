# Política de Pull Request

## PR da Task para develop

Toda task deve abrir PR da branch de trabalho para `develop`.

O PR deve conter:

- task;
- objetivo;
- escopo;
- fora do escopo;
- migrations;
- testes executados;
- resultados;
- documentação;
- auditoria;
- mensagens da API;
- riscos;
- limitações;
- screenshots quando aplicável;
- devices testados;
- checklist;
- plano de rollback.

## Merge em develop

Somente após:

- revisão concluída;
- CI aprovado;
- testes backend aprovados;
- testes Flutter aprovados;
- migration validada;
- documentação atualizada;
- `make check-task TASK=<TASK-ID>` aprovado;
- ausência de secrets;
- ausência de conflitos;
- aprovação manual.

Preferir squash and merge quando a branch possuir commits intermediários sem valor histórico.

Preservar merge commit quando for importante manter a composição completa da branch.

## PR develop para main

Somente após validação integrada em `develop`:

```text
develop
   ↓
Pull Request
   ↓
main
```

Não realizar merge local direto sem revisão.
