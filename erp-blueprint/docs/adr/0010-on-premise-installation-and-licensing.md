# ADR 0010: On-Premise Installation and Licensing

## Status

Accepted for product behavior; implementation details remain open.

## Context

DOC-008 defines On-Premise as the same ERP running in the customer's
environment, recommends Linux for the production server, and keeps `Company`
as the tenant root. The product needs an installation wizard that distinguishes
deployment services from licensed business modules, as well as time-limited
activation and remote revocation.

## Decision

- The ERP remains one modular product and codebase. An installation wizard
  configures deployment services separately from product-module entitlements.
- Business modules must be authorized by the backend; client-side visibility is
  not an entitlement boundary.
- Production On-Premise servers remain Linux-first. Windows with Docker Desktop
  is suitable for development and QA, not the recommended customer production
  server.
- Licenses are time-limited. If an installation cannot validate or renew because
  it is offline, it receives a maximum 30-day grace period from the last
  successful validation. After grace, writes are blocked while authorized read
  and export remain available. A server-side confirmation of expiry is not
  masked by an offline grace period.
- A verified remote revocation blocks all ERP access, including reads and
  exports, after the deployment receives the command. The database and backups
  must remain intact and unmodified by the lock.
- Remote commands cannot reach a deployment while it is disconnected. No
  immediate revocation guarantee may be made for an offline installation.
- The product must not claim that customer-controlled software is impossible to
  copy, patch, or crack. Use layered tamper resistance and detection without
  destructive DRM.
- Reactivation and recovery procedures are prerequisites to enabling remote
  revocation for customers.

## Consequences

- The wizard, licensing service, signed grants, module enforcement, expiry
  handling, remote commands, and reactivation each require implementation
  tasks, test coverage, and operational documentation.
- The signature format, signing algorithm, key rotation, activation interval,
  offline import flow, clock-tampering policy, deployment migration, recovery
  authorization, and exact service/module catalogs remain to be decided in the
  implementation design.
- An offline installation can continue locally during its grace period, but a
  remote command issued while it is offline cannot be acted on until it
  reconnects.
- A global remote lock prevents reads and exports through the ERP, so customer
  data preservation depends on keeping the database and backup paths intact.
- None of these decisions changes tenant identity, the approved authentication
  contract, or the order of existing commercial tasks.
