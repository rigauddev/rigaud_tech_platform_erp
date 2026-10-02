# Deployment And Distribution Architecture

## Ideia Principal

Tenant e deployment sao coisas diferentes.

Tenant e a empresa cliente.

Deployment e onde o ERP roda.

## Exemplo

```text
Company/Tenant: Restaurante Sabor da Serra
Deployment: CLOUD_SHARED
```

Futuramente o mesmo tenant pode migrar para:

```text
ON_PREMISE
HYBRID
CLOUD_DEDICATED
```

sem trocar a empresa oficial do sistema.

## Por Que Isso Importa

Essa separacao permite:

- SaaS compartilhado;
- clientes dedicados;
- servidor local;
- operacao sem internet;
- sincronizacao futura;
- migracao entre modelos;
- preservacao de auditoria e historico.

## Regra De Login

Usuario comum informa email e senha.

O backend resolve empresa, filial, papel e permissoes.

## Regra De Plataforma

Web, Android, iOS, Windows, macOS e Linux acessam o mesmo ERP.

Nao existem produtos separados por plataforma.
