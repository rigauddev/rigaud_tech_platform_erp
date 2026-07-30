# Users Tests

Cobertura criada na DEV-007:

- Validação de email, texto e telefone.
- Criação administrativa de usuário.
- Listagem e busca.
- Atualização de perfil administrativo.
- Perfil próprio.
- Bloqueio e revogação de sessões.
- Unicidade de email por empresa.
- Tentativas inválidas de login.
- Reset de contador em login válido.

Comandos:

```bash
docker compose exec -T backend pytest tests/unit/users tests/integration/users -q
docker compose exec -T backend pytest -q
```
