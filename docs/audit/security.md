# Audit Security

Somente superusuários consultam auditoria.

Eventos são sanitizados e não armazenam:

- senha;
- token;
- hash de refresh token;
- authorization header.
