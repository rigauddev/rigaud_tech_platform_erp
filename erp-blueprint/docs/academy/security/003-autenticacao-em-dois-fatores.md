# Autenticação em Dois Fatores

2FA combina senha com um segundo fator.

Na Rigaud Tech Platform ERP, TOTP é o canal recomendado. Email e SMS são canais adicionais, com riscos ligados à conta de email e à operadora.

O backend nunca deve emitir tokens finais antes de validar o segundo fator quando MFA está ativo.
