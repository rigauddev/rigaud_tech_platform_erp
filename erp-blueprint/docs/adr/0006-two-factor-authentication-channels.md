# ADR 0006: Canais de Autenticação em Dois Fatores

## Status

Aceita.

## Contexto

A plataforma já possui autenticação JWT e usuários multi-tenant. O próximo reforço de segurança será autenticação em dois fatores configurável.

## Decisão Proposta

DEV-009 permite habilitar ou desabilitar 2FA por usuário usando:

- email;
- telefone;
- aplicativo autenticador TOTP.

O fluxo reutiliza request_id, auditoria, catálogo de mensagens e respostas padronizadas criados na DEV-008.

TOTP é o canal recomendado. Email e SMS existem como canais adicionais, isolados atrás de interfaces de provider.

Segredos TOTP são criptografados antes de persistir. OTP e recovery codes são armazenados apenas por hash. Challenges temporários usam Redis preferencialmente, com fallback local apenas para desenvolvimento/teste.

Tokens finais são emitidos somente após validação do segundo fator quando o usuário possui MFA ativo.

## Consequências

Módulos futuros devem reutilizar os eventos e mensagens MFA sem criar novo contrato de autenticação.

WebAuthn, Passkeys, dispositivos confiáveis, push approval e SSO ficam fora desta decisão.
