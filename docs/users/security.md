# Users Security

## Autorização Temporária

Nesta etapa, apenas `is_superuser` administra usuários.

Usuários comuns podem:

- consultar o próprio perfil;
- editar campos básicos do próprio perfil;
- trocar a própria senha.

## Sessões

As sessões são revogadas quando:

- usuário é bloqueado;
- usuário é desativado;
- usuário troca a própria senha;
- superusuário reseta a senha.

## Senhas

As senhas usam a política já definida no módulo Auth.
Nenhum hash é retornado pela API.
