# Convenção de Commits

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

Exemplos:

```text
feat(products): implement multi-tenant product management
test(products): cover product uniqueness and permissions
docs(products): document product business rules
```

Não incluir secrets, tokens, `.env`, dumps de banco, artefatos de build ou arquivos temporários.
