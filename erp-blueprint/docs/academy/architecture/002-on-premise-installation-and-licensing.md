# On-Premise Installation and Licensing

## Learning Objective

Understand how an installation wizard can configure an On-Premise deployment
without turning product modules into separate ERP products or confusing a
deployment with its tenant.

## Deployment Services and Product Modules

Infrastructure services make the deployment run. Examples include the
application backend, database, cache, reverse proxy, and browser frontend.
Development tools such as PgAdmin and Mailpit are not production modules.

Restaurant and other business capabilities are product modules. They use the
same ERP codebase and are enabled by server-enforced entitlements. Hiding a
screen in Flutter is not sufficient to protect an API operation.

## License Lifecycle

A deployment receives a time-limited license grant that the server can verify.
If the licensing service is unreachable, the approved policy allows up to 30
days of offline operation. After that grace period, writes stop while authorized
read and export remain available.

A verified remote revocation is different from an internet outage. It blocks
all ERP application access, including reads and exports, after the deployment
receives the signed command. Customer database and backups remain preserved.
A disconnected server cannot receive a new remote command until it reconnects.

## Security Limit

No software installed on hardware administered by a customer can be promised to
be impossible to copy or modify. Cryptographic license verification, backend
authorization, auditing, protected vendor signing keys, and secure updates make
unauthorized changes harder and more detectable; they do not remove the server
owner's control of the machine.

## References

- [Deployment and Distribution Architecture](../../architecture/deployment-distribution-architecture.md)
- [ADR 0010](../../adr/0010-on-premise-installation-and-licensing.md)
