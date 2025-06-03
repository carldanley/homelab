<div align="center">

<img src="https://avatars.githubusercontent.com/u/1470571" align="center" width="144px" height="144px"/>

</div>

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f4a1/512.gif" alt="💡" width="20" height="20"> Overview

This repository is for my homelab infrastructure & Kubernetes clusters. I do the best I can to adhere to IaC (Infrastructure as Code) and GitOps best practices using tools like [Kubernetes](https://github.com/kubernetes/kubernetes), [Flux](https://github.com/fluxcd/flux2), [Renovate](https://github.com/renovatebot/renovate) and [GitHub Actions](https://github.com/features/actions).

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f331/512.gif" alt="🌱" width="20" height="20"> Kubernetes

This semi hyper-converged cluster operates on [Talos Linux](https://github.com/siderolabs/talos), an immutable and ephemeral Linux distribution tailored for [Kubernetes](https://github.com/kubernetes/kubernetes), and is deployed on bare-metal [MS-A2](https://store.minisforum.com/products/minisforum-ms-a2) workstations. [Rook](https://github.com/rook/rook) supplies my workloads with persistent block, object, and file storage, while a separate server handles media file storage & long term block storage backups. The cluster is designed to enable a full teardown without any data loss.

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/2699_fe0f/512.gif" alt="⚙" width="20" height="20"> Hardware

| Device                                 | Count | OS Disk Size | Data Disk Size | RAM  | Operating System | Purpose                 |
|----------------------------------------|-------|--------------|----------------|------|------------------|-------------------------|
| MinisForum MS-A2 (AMD Ryzen™ 9 9955HX) | 3     | 500GB M.2    | 1.92 TB U.2    | 96GB | Talos            | Kubernetes              |
| Synology DS918+                        | 1     | 4x8TB HDD    | -              | 4GB  | DSM 7            | NAS                     |
| PiKVM (RasPi 4)                        | 1     | 64GB (SD)    | -              | 4GB  | PiKVM            | KVM                     |
| TESmart 8 Port KVM Switch              | 1     | -            | -              | -    | -                | Network KVM (for PiKVM) |
| UniFi UDM Pro Max                      | 1     | -            | -              | -    | UniFi OS         | Router & NVR            |
| UniFi USW Aggregation                  | 1     | -            | -              | -    | UniFi OS         | 10G Core Switch         |

---
