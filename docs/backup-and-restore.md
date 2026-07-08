# Backup and Restore

Persistent volume backups are handled by Kopiur and Kopia.

## Repository

- Kopiur system namespace: `kopiur-system`
- Cluster repository: `ClusterRepository/r2`
- Kopia storage bucket: `batcave-kopia-backups`
- 1Password item: `kopia-storage`
- Kopia UI: `https://kopia.${DOMAIN_5}`

The repository is read/write for Kopiur, while the internal Kopia UI is
read-only and intentionally configured with insecure auth because it is exposed
only through the internal Gateway.

## Components

Apps opt into backups with these Kustomize components:

- `kubernetes/components/kopiur`
- `kubernetes/components/kopiur-restore`

The backup component creates a `SnapshotPolicy` and `SnapshotSchedule`. The
restore component creates the app PVC from a Kopiur `Restore`, which points at
the latest snapshot from the app policy.

Default policy behavior:

- schedule: `H * * * *` with `30m` jitter
- retention: `24` hourly snapshots and `7` daily snapshots
- quick verification: daily around `03:00`
- deep verification: monthly on the first day around `05:00`
- snapshot class: `csi-ceph-block`
- restore PVC size: `5Gi`, override with `KOPIUR_CAPACITY`

## Restore Procedure

Kopiur `Restore` resources resolve and pin a snapshot when they are created.
To restore the latest snapshot in an existing cluster, recreate both the
`Restore` and the app PVC.

Replace `NAMESPACE`, `APP`, and controller type/name as needed.

```sh
kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE patch helmrelease APP \
  --type=merge -p '{"spec":{"suspend":true}}'

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE scale deployment APP \
  --replicas=0

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE wait pod \
  -l app.kubernetes.io/name=APP --for=delete --timeout=5m

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE patch \
  kustomization.kustomize.toolkit.fluxcd.io APP \
  --type=merge -p '{"spec":{"suspend":true}}'

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE delete \
  restores.kopiur.home-operations.com APP --ignore-not-found

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE delete pvc APP

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE patch \
  kustomization.kustomize.toolkit.fluxcd.io APP \
  --type=merge -p '{"spec":{"suspend":false}}'

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE annotate \
  kustomization.kustomize.toolkit.fluxcd.io APP \
  reconcile.fluxcd.io/requestedAt="$(date +%s)" --overwrite
```

Wait for the restore and PVC:

```sh
kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE get \
  restores.kopiur.home-operations.com APP

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE get pvc APP
```

Bring the app back:

```sh
kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE patch helmrelease APP \
  --type=merge -p '{"spec":{"suspend":false}}'

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE scale deployment APP \
  --replicas=1

kubectl --kubeconfig kubernetes/kubeconfig -n NAMESPACE rollout status \
  deployment APP --timeout=10m
```

If the app uses a StatefulSet or a controller label that differs from the app
name, adjust the scale, wait, and rollout commands accordingly.

## Verification

Check policy freshness and failures:

```sh
kubectl --kubeconfig kubernetes/kubeconfig get snapshotpolicies.kopiur.home-operations.com -A
kubectl --kubeconfig kubernetes/kubeconfig get snapshotschedules.kopiur.home-operations.com -A
kubectl --kubeconfig kubernetes/kubeconfig get snapshots.kopiur.home-operations.com -A
kubectl --kubeconfig kubernetes/kubeconfig get restores.kopiur.home-operations.com -A
```

The same status view is available through:

```sh
task kopiur:status
```

Create a pinned manual snapshot:

```sh
task kopiur:snapshot NS=media APP=tautulli
```

Useful Prometheus metrics:

- `kopiur_policy_last_backup_success_timestamp_seconds`
- `kopiur_policy_last_backup_size_bytes`
- `kopiur_snapshot_consecutive_failures`
- `kopiur_resource_phase`
- `kopiur_controller_reconcile_errors_total`

The Kopiur Helm chart installs its own `ServiceMonitor`, `PrometheusRule`, and
Grafana dashboard. This repository also adds homelab-specific alerting in
`kubernetes/apps/kopiur-system/kopiur/repository/prometheusrule.yaml`.

## Post-Migration Cleanup

VolSync and Restic are no longer used for application PVC backups.

Manual cleanup candidates after the Kopiur retention window has had time to
settle:

- 1Password item: `volsync`
- R2 target: the bucket or prefix referenced by the `REPO_PREFIX` field in the
  `volsync` 1Password item

Do not delete:

- `kopia-storage` in 1Password
- `batcave-kopia-backups`
- `calamityxi-mariadb-api-server`
- `calamityxi-mariadb-early-access`

The CalamityXI buckets are used by MariaDB operator `PhysicalBackup` resources,
not by the old VolSync provider.
