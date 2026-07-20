# Woodpecker CI

Woodpecker runs in the dedicated `woodpecker-system` namespace and uses Gitea
for authentication and repository discovery. The Gitea OAuth callback is:

```text
https://ci.${DOMAIN_7}/authorize
```

The Woodpecker administrator is supplied by the 1Password-backed runtime
Secret. Registration is closed; users who can authenticate through Gitea may
use repositories they can access there.

## Image builds

Pipeline steps run as Kubernetes pods. The agent is intentionally unable to
select arbitrary service accounts or read native Kubernetes secrets. Do not
mount a Docker socket or use the shared privileged BuildKit daemon.

For ordinary compilation and tests, run images as their non-root UID. For an
image-producing step, opt into a user namespace so UID 0 exists only inside the
pipeline pod and maps to an unprivileged host UID:

```yaml
backend_options:
  kubernetes:
    hostUsers: false
    securityContext:
      runAsUser: 0
      runAsGroup: 0
      allowPrivilegeEscalation: false
```

This is suitable for daemonless OCI builders that support user namespaces. It
does not grant host root and does not expose a container runtime socket. Keep
the builder's capabilities dropped unless its documentation identifies a
specific required capability.

Publish private images to Gitea's existing OCI registry:

```text
git.${DOMAIN_7}/<owner>/<image>:<tag>
```

Gitea remains the source of truth for private images. Spegel transparently
caches pulls between cluster nodes; it is not a registry and should not be used
as a push target. Gitea's package cleanup job and storage alerts provide the
retention and capacity controls for this registry.

Woodpecker has a dedicated Gitea package service account. Its narrowly scoped
package token is stored only in 1Password and exposed to trusted builds as the
global `gitea_registry_username` and `gitea_registry_token` secrets. These
secrets are not available to pull-request events. Woodpecker also uses the
credential for private pipeline-image pulls, and Talos uses it for private pod
image pulls. Spegel then caches successful pulls across nodes.

Go services that do not need a custom Containerfile can use `ko` without a
daemon or root. Go services with custom filesystem layouts and Rust services
should use the same pinned, daemonless OCI builder image so both languages have
one reproducible publishing path.

## Availability and capacity

Two agents run on separate nodes, each accepting one workflow at a time. Agent
configuration is stored on `ceph-block` volumes so restarts do not discard it.
The namespace has default container requests and limits plus a ResourceQuota;
this prevents an unbounded build queue from consuming the cluster while still
leaving room for bursty Go and Rust compilation.

Prometheus scrapes the authenticated Woodpecker metrics endpoint. Alerts cover
server availability, connected workers, sustained queueing, and unavailable
agent replicas.

## Backups and recovery

Woodpecker's durable state is in the shared CloudNativePG `woodpecker` database.
It is included in the daily object-storage backup and continuous WAL archive;
the cluster retains backups for 30 days. Prometheus alerts if the latest usable
backup becomes older than 36 hours or a failed backup is newer than the latest
successful backup.

For recovery, restore the shared CloudNativePG cluster to a new cluster from the
latest object-store backup, verify the `woodpecker` database and table counts,
then point a temporary Woodpecker server at the recovered database. Keep the
production server stopped during a real cutover so two servers never write to
the same restored database. Run this restore drill after material database or
backup-plugin changes and at least quarterly.
