# Auth/Tenant Alignment

Esta aula registra a regra operacional oficial da DEV-012.

O usuário autenticável do ERP pertence a uma única empresa e possui uma filial ativa única. Isso simplifica login, auditoria, estoque, pedidos e permissões do MVP.

O frontend envia apenas email e senha. O backend encontra o usuário, valida a empresa, resolve a filial ativa e emite JWT com `user_id`, `tenant_id`, `branch_id` e `role`.

Usuário comum não troca filial. Quando uma mudança for necessária, ela deve ser feita por gestor, administrador ou permissão explícita, com registro em histórico.

Essa decisão evita ambiguidade antes de REST-003 e mantém `tenant_id` presente em todas as tabelas relevantes para SaaS e On-Premise.
