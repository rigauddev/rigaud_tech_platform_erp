# On-Premise Installation Wizard and Licensing

DOC-012 defines the product and security boundaries for a future On-Premise
installation wizard and license lifecycle. This document is an architecture
specification; it does not implement an installer, license server, activation
API, or runtime lock.

## Product Boundaries

- An On-Premise deployment is the same Rigaud Tech Platform ERP product, not a
  fork or a separate ERP for each customer.
- Linux is the recommended production server. Windows with Docker Desktop is a
  development and QA environment, not the supported production-server target.
- A `Company` remains the tenant. A deployment installation identifier is
  separate from the tenant and must not replace `tenant_id = companies.id`.
- The current backend is a modular application. Business modules are not
  separate Docker services merely because a customer enables them.

## Wizard Responsibilities

The wizard must present two separate choices:

1. **Deployment services**: the infrastructure and application components
   required to operate the chosen deployment.
2. **Product modules**: the capabilities the customer's license enables.

The selection must not imply that optional infrastructure is a commercial
module, or that hiding a module in Flutter secures its API.

### Service Selection

The initial production profile should keep the services required by the
existing architecture together: reverse proxy, backend, PostgreSQL, and Redis.
The web frontend is included when the selected deployment serves the browser
client. Additional services may be offered only when their operational purpose,
resource impact, backup needs, and support policy are documented.

Mailpit and PgAdmin are development tools and must not be exposed as customer
production services by default. The wizard must not create a second Compose
project or rename the official Compose project.

### Module Selection

The wizard may select licensed business capabilities, such as Restaurant, but
must resolve module prerequisites from an explicit dependency map. The
selection does not install a different codebase. The backend must enforce
entitlements for API operations; a hidden navigation item or local Flutter flag
is not an authorization boundary.

### Initial Wizard Flow

1. Check supported operating system, CPU architecture, disk, memory, ports,
   container runtime, and connectivity requirements.
2. Choose the deployment profile and required/optional infrastructure services.
3. Choose product modules and validate their dependencies against the license.
4. Create or identify the deployment installation; do not silently create a
   second tenant.
5. Activate a license online or import a signed offline activation response.
6. Configure network exposure, TLS, administrator access, secrets, and backup
   location.
7. Display the complete installation plan and obtain explicit confirmation.
8. Start or update the existing deployment, apply migrations, and verify health
   checks before reporting success.
9. Show recovery, backup, update, license status, and support instructions.

The wizard must fail visibly when a prerequisite or health check fails. It must
not report a successful installation while migrations or required services
remain unhealthy.

## License and Entitlement Model

The license service is separate from business-module code. A signed license
grant should identify the customer/company, deployment installation, allowed
modules, issue time, expiry, license version, and offline policy. Final payload
fields, signature algorithm, key rotation, and customer migration rules must be
confirmed during the implementation task.

The vendor signing private key must never be shipped to customer installations.
Customer servers verify grants using a public key and enforce entitlements in
the backend. Activation keys are not passwords and must not be logged or stored
in plaintext after activation. Online activation uses authenticated TLS.
Offline activation uses a deployment-generated challenge and a vendor-signed
response; manually transferring an activation file does not make an unsigned
grant trusted.

License states to implement:

- `PENDING_ACTIVATION`
- `ACTIVE`
- `OFFLINE_GRACE`
- `EXPIRED_READ_ONLY`
- `REMOTELY_LOCKED`

The license term is time-limited. When loss of connectivity prevents renewal or
validation, the deployment may continue for at most 30 days from its last
successful validation. After that grace period, new writes are blocked while
authorized read and export remain available. If an online validation confirms
that the license has expired, the deployment applies the expired policy without
pretending that an offline grace period can change the confirmed license term.

## Remote Revocation and Data Preservation

A remote revocation is a signed, auditable command scoped to one deployment.
The implementation must authenticate the command, reject invalid or replayed
commands, and record its receipt and result. The implementation task must
define command expiry, sequencing, authorization, and recovery.

The approved product behavior is:

- A valid remote revocation blocks all ERP application access, including reads
  and exports, once the deployment receives and verifies the command.
- Revocation never deletes or encrypts the PostgreSQL database, backups, or
  customer files.
- A deployment with no network connection cannot receive a new remote command.
  Therefore, remote revocation cannot be promised as immediate for a
  disconnected installation.
- Loss of licensing connectivity alone follows the 30-day offline policy above;
  it is not a remotely received revocation.

The implementation must document an authorized reactivation and incident
recovery procedure before remote revocation is enabled for customers.

## Security Limits and Controls

Software running on customer-controlled hardware cannot be guaranteed to be
impossible to copy, patch, or crack. Do not make such a guarantee. Signed
entitlements, server-side authorization, audit, protected signing keys, secure
updates, least privilege, TLS, backups, and monitoring reduce casual
tampering and improve detection, but do not remove the customer's administrative
control of its own server.

Do not bind a license solely to a mutable hardware identifier. The
implementation must define safe reactivation after server replacement or
disaster recovery without changing the tenant identity or losing customer data.
Do not add destructive expiry behavior, data deletion, or database encryption
controlled by a remote lock.

## Scope Boundaries

This architecture task does not implement:

- the installation wizard or deployment service profiles;
- licensing APIs, license server, key issuance, or revocation commands;
- service/module entitlements, subscription billing, or payment integration;
- production support for a Windows-hosted ERP server;
- backup/restore, unattended upgrades, or disaster recovery automation.

Those items require separately scoped implementation tasks with tests,
operational documentation, and explicit recovery procedures.

## Decisions Still Required for Implementation

- License term catalog and renewal rules.
- Online validation interval and behavior for clock rollback.
- Signature algorithm, key rotation and trust-anchor update strategy.
- Offline activation/import workflow and support responsibilities.
- Safe deployment migration and license reactivation process.
- Administrator recovery when a remotely revoked deployment is inaccessible.
- Exact Compose profiles, supported Linux distributions, resource minimums,
  TLS provisioning, backup/restore, upgrades, and rollback.
- Module dependency map and API-level entitlement coverage.
