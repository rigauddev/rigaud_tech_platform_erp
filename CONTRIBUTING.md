# Contributing

Contribuições na Rigaud Tech Platform ERP seguem a regra:

```text
Uma Task
Um Prompt
Uma Entrega
```

## Repositório Oficial

```text
https://github.com/rigauddev/rigaud_tech_platform_erp.git
```

## Branches Permanentes

- `main`: código validado, estável e apto para produção.
- `develop`: integração das tasks concluídas e revisadas.

Não desenvolver diretamente em `main` ou `develop`.

## Branches de Trabalho

Padrão:

```text
feature/<task-id>-<descricao>
fix/<task-id>-<descricao>
docs/<task-id>-<descricao>
hotfix/<descricao>
release/<versao>
```

Exemplo:

```text
feature/rest-001-products
```

## Fluxo Obrigatório

```text
develop
   ↓
feature/<task-id>-<descricao>
   ↓
commit
   ↓
push
   ↓
Pull Request para develop
   ↓
validação
   ↓
merge em develop
   ↓
validação completa
   ↓
Pull Request develop para main
   ↓
merge em main
   ↓
tag da versão, quando aplicável
```

## Commits

Formato:

```text
<tipo>(<escopo>): <descrição>
```

Tipos permitidos:

- `feat`
- `fix`
- `docs`
- `test`
- `refactor`
- `chore`
- `build`
- `ci`
- `perf`
- `security`

## Proibido

- push direto em `main`;
- push direto em `develop`;
- misturar duas tasks na mesma branch;
- commit de secrets, `.env`, tokens, chaves, banco local ou artefatos temporários.
