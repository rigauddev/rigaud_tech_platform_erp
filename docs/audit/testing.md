# Audit Testing

Comandos:

```bash
docker compose exec -T backend pytest tests/unit/governance tests/integration/audit -q
docker compose exec -T backend pytest -q
```
