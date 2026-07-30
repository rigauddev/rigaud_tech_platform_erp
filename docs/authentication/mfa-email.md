# MFA por Email

Email OTP usa código temporário, hash no challenge e expiração curta.

Em desenvolvimento, o adapter pode enviar para Mailpit. Em produção, provider real deve estar configurado; envio falso é bloqueado.

O email completo não é exposto nos fluxos públicos quando não necessário.
