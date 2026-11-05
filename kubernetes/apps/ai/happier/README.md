# Happier deployment foundation

**Draft: deployment and HA acceptance remain blocked.**

## Included

Retained CNPG Database and basic-auth ExternalSecret manifests in `databases`,
plus private-DNS manifests and two **suspended** Flux Kustomizations. No relay,
Redis, Service, route, storage or network allow is implemented or deployed.
The shared PostgreSQL Cluster is unchanged: the Happier managed role is explicitly
pending, so this foundation cannot activate a role before its password exists.

## Required user inputs BEFORE MERGE
Create a NEW proposed 1Password item `happier` with independent strong fields
`postgrespassword` and `servermastersecret`. These are proposed names, not guessed
existing references. Confirm these references with the user before enabling reconciliation. Never commit values.
Only postgrespassword is consumed here into databases/happier-database-secret;
servermastersecret is reserved for the future app and not wired yet. No vault
credentials were read. Resume database Flux only after ESO/CNPG dependencies and
secret readiness are gated; suspended database resources do not supply the role
secret until resumed. Add the least-privilege managed `happier` role only after
`databases/happier-database-secret` is Ready, then reconcile the Database. Split
secret provisioning from Database creation and gate the shared Cluster dependency
before activation; the current suspended scaffold does not implement this sequence.

## Blocking design review
Full relay storage and the client-readable file URL auth/privacy boundary remain
unresolved. S3 requires client-readable unsigned URLs, not presigned URLs; NEVER
enable public Internet bucket reads. CephFS RWX plus an internal file endpoint is
only a candidate requiring review, not an approved design. Do not assume E2EE.
The target is two API replicas plus one worker using the existing three-instance
PostgreSQL cluster; no API or worker workloads are implemented here. Two relay
replicas do not establish HA. Redis accepts a Redis URL, not Sentinel
discovery; stable primary endpoint and failover infrastructure remain required.
Add migration gate, application secret, internal route and narrow Coder backend
access together with the actual relay. DNS alone is not authentication/isolation.
No speculative network allow is installed without the application selectors.

A verified immutable container image, executable path, migration command and
API/worker startup arguments remain release blockers; this foundation pins none.
Use existing postgres primary service with dedicated happier credentials, not
coder role. Database retention is not a backup or complete recovery plan.

## Resource planning

No new Pods or PVCs are requested by this suspended foundation. Initial planning
estimate only: two APIs at 250m CPU/512Mi each, one worker at 250m CPU/512Mi,
plus Redis at 100m CPU/256Mi per member. Redis topology, limits, persistent capacity
and PostgreSQL connection budget require measurement and review; these are not
implemented requests or validated production sizing. Reuse the existing
three-instance PostgreSQL cluster rather than claiming new database capacity.

## Acceptance before activation

Before enabling: resolve storage/privacy and HA choices, add dependency gates,
render/schema validation and real migration/readiness/isolation/failover tests.
Source-only scaffold; no merge, live apply, secret writes or runtime HA claim.
