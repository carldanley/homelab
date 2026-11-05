# Homelab workspace access (source proposal)

Prerequisites: reviewed GitOps changes, existing Cilium/CoreDNS conventions,
and the prepared `dev-workspace-images/templates/homelab` template/image.
Explicit approval is required before merge, reconciliation, template activation,
or live acceptance. Authoring performs no automatic sync/apply.

The template uses namespace `homelab-workspaces`, ServiceAccount
`homelab-workspace`, and ConfigMap `homelab-kubeconfig` key `config` mounted
at `/etc/homelab/config`, with `KUBECONFIG` set accordingly. Authentication uses
the projected token and cluster CA, not embedded credentials. The default
diagnostic namespace is `coder-workspaces`.

Only `coder/coder` provisions Deployments/PVCs in the new namespace; its narrow
namespaced provisioner Role is unchanged. PSA is restricted.

The proposed ClusterRole and ClusterRoleBinding `homelab-workspace-reader` bind
only ServiceAccount `homelab-workspace` in `homelab-workspaces`. Diagnostics are
curated cluster-wide reads (across namespaces), not access to every object.
Explicit get/list/watch grants:

| API group | Resources |
| --- | --- |
| core | namespaces, nodes, pods, services, endpoints, persistentvolumeclaims, persistentvolumes, events |
| apps | deployments, replicasets, statefulsets, daemonsets, controllerrevisions |
| batch | jobs, cronjobs |
| networking.k8s.io | ingresses, ingressclasses, networkpolicies |
| discovery.k8s.io | endpointslices |
| storage.k8s.io | storageclasses, volumeattachments, csidrivers, csinodes, csistoragecapacities |
| policy | poddisruptionbudgets |
| autoscaling | horizontalpodautoscalers |
| events.k8s.io | events |
| source.toolkit.fluxcd.io | gitrepositories, ocirepositories, helmrepositories, helmcharts, buckets |
| kustomize.toolkit.fluxcd.io | kustomizations |
| helm.toolkit.fluxcd.io | helmreleases |
| cilium.io | ciliumnetworkpolicies, ciliumclusterwidenetworkpolicies |

Exceptions: core `pods/log` is get-only; metrics.k8s.io `pods` and `nodes` are
get/list-only. All unlisted resources are excluded, including Secrets,
ConfigMaps, ServiceAccounts, RBAC objects, external-secrets and notification
resources. No writes (including status), exec, attach, port-forward,
ephemeralcontainers, node/service proxy, token requests, impersonation,
bind/escalate, nonResourceURLs or wildcards are granted.

Read-only is not secret-proof: Pod specs, logs, workload templates, events and
other permitted objects can expose application credentials or sensitive data.
All code running in this workspace can use the identity; restrict who can run it.
The kubeconfig namespace is only a default; for example `kubectl get pods -A`
uses the curated cluster-wide permissions.

Networking defaults to denied ingress/egress, permitting CoreDNS, existing
Coder control-plane access, public IPv4 excluding existing private/reserved
ranges, and `kube-apiserver` TCP 443/6443. Additive policies do not replace RBAC.

`kubernetes/flux/cluster/ks.yaml` already targets `./kubernetes/apps`.
Without a global apps kustomization, Flux generates recursive discovery.
The new namespace root references its child Flux Kustomization; no global
apps kustomization is needed.

The owner must approve the source changes through a PR before merge and Flux
application; this proposal does not authorize either action.
After separate approval, verify allowed curated reads across namespaces and
cluster-scoped resources, and denied Secrets, ConfigMaps, Pod creation/deletion,
exec and unlisted resources using the actual workspace identity. Check API/DNS reachability and private-network
denial. Offline rendering cannot prove runtime authorization or connectivity.
