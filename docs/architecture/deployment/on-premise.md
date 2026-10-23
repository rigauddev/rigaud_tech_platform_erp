# On-Premise Deployment

On-Premise significa deployment local do cliente. O produto continua sendo o mesmo ERP.

## Arquitetura Recomendada

```text
Clientes
  ↓
Rede Local
  ↓
Servidor ERP
  ├── Nginx
  ├── FastAPI
  ├── PostgreSQL
  └── Redis
```

## Servidor

O servidor de producao recomendado para On-Premise e Linux.

Windows, macOS, Linux, Android e iOS sao plataformas de acesso. Elas nao definem o sistema operacional recomendado para o servidor de producao.

## Banco

Cada instalacao On-Premise deve possuir um PostgreSQL local do deployment.

O tenant continua sendo a empresa cliente, e `tenant_id = companies.id` permanece obrigatorio para preservar compatibilidade com SaaS, migracao e futuras sincronizacoes.

## Operacao Local

Quando a internet estiver indisponivel, mas a rede local e o servidor local estiverem funcionando, os clientes devem continuar acessando o ERP normalmente pelo deployment local.

## Responsabilidades Futuras

- wizard para selecionar servicos de deployment e modulos comerciais licenciados;
- ativacao de licenca assinada, prazo, carencia offline de 30 dias e revogacao remota;
- backup local;
- restauracao;
- atualizacao assistida;
- monitoramento;
- sincronizacao com cloud quando habilitada;
- politica de licenca e entitlements offline.

O comportamento aprovado e os limites de seguranca estao em
[On-Premise Installation Wizard and Licensing](./on-premise-installation-and-licensing.md)
e [ADR 0010](../../../erp-blueprint/docs/adr/0010-on-premise-installation-and-licensing.md).
Esses itens continuam planejados; esta documentacao nao afirma que o wizard ou o
licenciamento ja existam.
