<div align="center">

<img src="https://avatars.githubusercontent.com/u/1470571" align="center" width="144px" height="144px"/>

</div>

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f4a1/512.gif" alt="💡" width="20" height="20"> Overview

This repository is for my homelab infrastructure & Kubernetes clusters. I do the best I can to adhere to IaC (Infrastructure as Code) and GitOps best practices using tools like [Kubernetes](https://github.com/kubernetes/kubernetes), [Flux](https://github.com/fluxcd/flux2), [Renovate](https://github.com/renovatebot/renovate) and [GitHub Actions](https://github.com/features/actions).

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f331/512.gif" alt="🌱" width="20" height="20"> Kubernetes

This semi hyper-converged cluster operates on [Talos Linux](https://github.com/siderolabs/talos), an immutable and ephemeral Linux distribution tailored for [Kubernetes](https://github.com/kubernetes/kubernetes), and is deployed on bare-metal [MS-A2](https://store.minisforum.com/products/minisforum-ms-a2) workstations. [Rook](https://github.com/rook/rook) supplies my workloads with persistent block, object, and file storage, while a separate server handles media file storage & long term object storage backups. The cluster is designed to enable a full teardown without any data loss.

There is a template at [onedr0p/cluster-template](https://github.com/onedr0p/cluster-template) if you want to follow along with some of the practices I use here.

### Core Components

- [actions-runner-controller](https://github.com/actions/actions-runner-controller) - Self-hosted GitHub runners
- [cert-manager](https://github.com/cert-manager/cert-manager) - Creates SSL certificates for services in my cluster
- [cilium](https://github.com/cilium/cilium) - eBPF-based networking for my workloads
- [cloudflared](https://github.com/cloudflare/cloudflared) - Enables Cloudflare secure access to my routes
- [external-dns](https://github.com/kubernetes-sigs/external-dns) - Automatically syncs ingress DNS records to a DNS provider
- [multus](https://github.com/k8snetworkplumbingwg/multus-cni) - Multi-homed pod networking
- [rook](https://github.com/rook/rook) - Distributed block storage for persistent storage
- [spegel](https://github.com/spegel-org/spegel) - Stateless cluster local OCI registry mirror
- [volsync](https://github.com/backube/volsync) - Backup and recovery of persistent volume claims

### GitOps

[Flux](https://github.com/fluxcd/flux2) watches my [kubernetes](./kubernetes) folder (see Directories below) and makes the changes to my clusters based on the state of my Git repository.

Flux will recursively search the [kubernetes/apps](./kubernetes/apps) folder until it finds the most top level `kustomization.yaml` per directory and then apply all the resources listed in it. That aforementioned `kustomization.yaml` will generally only have a namespace resource and one or many Flux kustomizations (`ks.yaml`). Under the control of those Flux kustomizations there will be a `HelmRelease` or other resources related to the application which will be applied.

[Renovate](https://github.com/renovatebot/renovate) monitors my **entire** repository for dependency updates, automatically creating a PR when updates are found. When a PR is merged Flux will automatically apply the changes to my cluster.

### Directories

This Git repository contains the following directories under [kubernetes](./kubernetes).

```sh
📁 kubernetes      # Kubernetes cluster defined as code
├─📁 apps          # Apps deployed into my cluster grouped by namespace (see below)
├─📁 components    # Re-usable kustomize components
└─📁 flux          # Flux system configuration
```

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/2699_fe0f/512.gif" alt="⚙" width="20" height="20"> Hardware

| Device                                 | Count | OS Disk Size | Data Disk Size | RAM  | Operating System | Purpose                 |
|----------------------------------------|-------|--------------|----------------|------|------------------|-------------------------|
| MinisForum MS-A2 (AMD Ryzen™ 9 9955HX) | 3     | 500GB M.2    | 1.92 TB U.2    | 96GB | Talos            | Kubernetes              |
| Synology DS918+                        | 1     | -            | 4x8TB HDD      | 4GB  | DSM 7            | NAS                     |
| PiKVM (RasPi 4)                        | 1     | 64GB (SD)    | -              | 4GB  | PiKVM            | KVM                     |
| TESmart 8 Port KVM Switch              | 1     | -            | -              | -    | -                | Network KVM (for PiKVM) |
| UniFi UDM Pro Max                      | 1     | -            | -              | -    | UniFi OS         | Router & NVR            |
| UniFi USW Aggregation                  | 1     | -            | -              | -    | UniFi OS         | 10G Core Switch         |

---

My MS-A2 workstations are configured with the following hardware:

- [Crucial 96GB Kit (48GBx2) DDR5-5600 SODIMM](https://www.crucial.com/memory/ddr5/ct2k48g56c46s5)
- [Crucial 500GB M.2 P3 Plus Gen4 NVMe PCIe 4.0](https://www.crucial.com/products/ssd/crucial-p3-plus-ssd) (Talos OS)
- [Samsung 1.92TB U.2 2.5-inch 7mmT PM9A3 NVMe PCIe 4.0](https://www.samsung.com/us/business/computing/memory-storage/enterprise-solid-state-drives/pm9a3-nvme-u-2-ssd-1-9tb-mz-ql21t900/) - (Ceph Storage)

---

My Synology DS918+ is configured with the following hardware:

- [Seagate IronWolf 8TB 3.5 Inch SATA 6Gb/s 7200 RPM 256MB Cache](https://www.seagate.com/www-content/product-content/ironwolf/en-us/docs/100844482b.pdf) - (Synology Hybrid RAID)
- [Samsung 990 PRO SSD 1TB PCIe 4.0 M.2 2280](https://www.samsung.com/us/computing/memory-storage/solid-state-drives/990-pro-pcie--4-0-nvme--ssd-1tb-mz-v9p1t0b-am.html) - (SSD Read/Write Caching)

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/270f_fe0f/512.gif" alt="🖍︎" width="20" height="20"> Additional Documentation

For random notes I've taken the time to jot down, see the following links:

- [Configuring DNS on UDM-Pro for Ad-blocking](./docs/configuring-dns-on-udm-pro-for-adblocking.md)
- [TESMART KVM Switch + PiKVM](./docs/tesmart-kvm-switch-and-pikvm.md)
- [Using Cilium with UniFi BGP](./docs/using-cilium-with-unifi-bgp.md)
- [Checking Synology SSD Cache](./docs/checking-synology-ssd-cache.md)

For fonts, see [Noto Emoji Animations](https://googlefonts.github.io/noto-emoji-animation/).

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f64f/512.gif" alt="🙏" width="20" height="20"> Gratitude and Thanks

Many thanks to all the fantastic people who donate their time to the [Home Operations](https://discord.gg/home-operations) Discord community. Be sure to check out [kubesearch.dev](https://kubesearch.dev) for ideas on how to deploy applications or get ideas on what you may deploy.

---

## <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/2696_fe0f/512.gif" alt="⚖" width="20" height="20"> License

See [LICENSE](./LICENSE).
