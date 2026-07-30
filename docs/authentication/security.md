# Authentication Security

## DEV-009 planejada

A próxima etapa transversal de segurança será autenticação em dois fatores.

Canais planejados:

- email;
- telefone;
- aplicativo autenticador.

O recurso deverá poder ser habilitado ou desabilitado conforme política do usuário/empresa e deverá reutilizar auditoria, `request_id`, catálogo de mensagens e respostas padronizadas da DEV-008.

## Tenant

O cliente informa `tenant` como slug/código.

O backend resolve internamente o `tenant_id`; o cliente nunca envia `tenant_id` confiável.

Enquanto o módulo de empresas não existe, `auth_users.tenant_slug` funciona como representação mínima técnica para resolver o tenant.

## RBAC e MFA

RBAC e MFA permanecem preparados na camada de segurança, mas não foram implementados nesta task.

## Dados Sensíveis

- Senhas nunca são retornadas pela API.
- Refresh token não é armazenado em texto puro.
- Access token é de curta duração.
- Refresh token é revogado em logout e rotacionado a cada uso.
