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

## Cargo dependency cache

Rust pipelines may use the cluster-local Rook object store at:

```text
http://rook-ceph-rgw-internal-cache.rook-ceph.svc:80
```

Rook owns this shared, cache-oriented RGW service and its `ceph-object-cache` bucket
StorageClass. Woodpecker owns only its namespaced bucket claim, lifecycle, and
credentials.

The `woodpecker-cargo-cache-v1` bucket claim creates a uniquely named bucket for
disposable build acceleration, not a backup. It has a 100 GB user quota, a
10,000-object limit, 30-day object expiration, and one-day cleanup for
incomplete multipart uploads. The bucket's metadata is triply replicated and
its archive data uses a 2+2 erasure-coded pool. There is no ingress or external
endpoint for the service.

Rook creates `Secret/woodpecker-cargo-cache-v1` and a same-named ConfigMap in
the `woodpecker-system` namespace. The ConfigMap's `BUCKET_NAME` value is
authoritative for the generated bucket name. Copy it and the generated access
key pair into Woodpecker-managed repository settings and secrets, or
organization-level values only when all participating repositories share the
same trust boundary. Keep native Kubernetes secrets disabled. Restrict the
credentials to push events and the exact digest of the reviewed cache plugin;
do not expose them to pull-request events. Anyone who can push pipeline changes
remains inside this trust boundary because Woodpecker secret event filters do
not restrict branches.
Load credential values with `woodpecker-cli --value @file`; never print them or
commit them to this repository.

The cache plugin image must be scanned, pinned by digest, and preferably
mirrored to Gitea before use. Restore and save steps must use `failure: ignore`,
and saves should run only after a successful default-branch build. Use a stable
key such as `cargo-v1-x86_64`; bump the version manually when the cache layout
needs to be replaced.

Cache only Cargo's reusable download data:

```text
registry/index
registry/cache
git/db
```

Do not cache `credentials.toml`, extracted registry or Git checkouts, or
`target/`. Stage the selected directories into a credential-free cache path if
the plugin accepts only one path. The crate archives and Git objects are already
compressed, so disable the plugin's gzip pass when the resulting archive stays
comfortably below the S3 single-PUT limit. If representative archives approach
5 GB, replace the plugin with a reviewed multipart-capable helper.

Rotate credentials and buckets blue/green: create a versioned replacement OBC,
load versioned Woodpecker secrets, warm and verify the replacement, switch the
pipelines, then remove the old secrets and OBC. To disable caching, first remove
the pipeline steps and secrets so builds immediately fall back to cold Cargo
downloads. In a separate reconciliation, prune the OBC and verify its
ObjectBucket, Secret, ConfigMap, and RGW bucket are gone. Remove the cache
Kustomization afterward. Keep the generic object store while any other cache
consumer uses it. Pool deletion remains a separate manual operation because
`preservePoolsOnDelete` is enabled.

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
