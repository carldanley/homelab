# Jellyfin on TrueNAS

Jellyfin runs alongside Plex on the MinisForum N5 Pro at `10.40.1.40`. The TrueNAS custom app is named `jellyfin`; its Compose definition is [truenas/jellyfin/compose.yaml](../truenas/jellyfin/compose.yaml). Flux manages the Kubernetes routing and DNS resources, not the NAS container.

## Access and accounts

- Server: <https://jellyfin.r1p.io>
- 1Password: **Jellyfin** in **Batcave Services (Private)** holds the playback login and separate admin credentials.
- Use `carldanley` for playback and `carldanley-admin` for server administration. Both require passwords; neither appears on the public login screen.
- Add individual accounts for other viewers from Dashboard → Users. Content deletion is disabled on the initial accounts.

Enter the same HTTPS URL in Jellyfin clients on Shield, Apple TV, phones, and browsers. On the Shield Pro 2019, test a known Dolby Vision / Atmos title with the receiver and television before replacing the existing Plex workflow. Server-side transcoding cannot establish that the entire HDMI chain is passing those formats correctly.

## Storage and hardware

The app runs as TrueNAS UID/GID `568:568` with supplemental render group `107`. The Intel Arc A310 at PCI `0000:c9:00.0` is mapped to `/dev/dri/renderD128` inside the container. The Compose mapping uses the stable PCI path; after hardware changes, verify this path and the render-group ID on the NAS.

Create these ZFS datasets with LZ4 compression, atime off, owner/group `568:568`, and mode `0750` before installing the custom app:

| Dataset | Container path | Purpose |
| --- | --- | --- |
| `zpool/jellyfin` | — | Parent dataset and deployment copy |
| `zpool/jellyfin/config` | `/config` | Accounts, configuration, database, metadata |
| `zpool/jellyfin/cache` | `/cache` | Cache |
| `zpool/jellyfin/transcodes` | `/transcodes` | Temporary streaming output |
| `zpool/jellyfin/recordings` | `/recordings` | New Jellyfin DVR recordings |

The existing media mounts are read-only:

| Library | NAS path | Container path |
| --- | --- | --- |
| Movies | `/mnt/zpool/media/movies` | `/data/movies` |
| TV Shows | `/mnt/zpool/media/series` | `/data/series` |
| Music | `/mnt/zpool/media/music` | `/data/music` |
| DVR | `/mnt/zpool/media/dvr` | `/data/dvr` |

Jellyfin uses Intel QSV hardware acceleration and HDR tone mapping. The transcode directory is `/transcodes`; throttling and old-segment removal are enabled. HEVC and AV1 encoding are allowed when supported by the client. Chapter images, trickplay generation, and audio loudness scanning are initially disabled to reduce background work during the trial. The container has an 8 GiB memory limit and an eight-CPU quota. Plex and Jellyfin share the physical GPU, so test combined demand before relying on several simultaneous 4K transcodes.

The HDHomeRun FLEX 4K (`10.20.133.199`) is configured as a four-tuner source. Plex and Jellyfin share those four physical tuners. New recordings go to `/recordings`; the existing Plex DVR library stays read-only. Guide listings need a separate Jellyfin-compatible XMLTV source or Schedules Direct account; Plex's guide subscription and scheduled recordings are not imported. DRM channels cannot be assumed to play in Jellyfin.

## HTTPS and DNS

Public traffic follows this path:

```text
jellyfin.r1p.io → home WAN TCP 443 → UniFi port forward
              → dedicated Cilium Gateway 10.50.50.3:443
              → Jellyfin service / EndpointSlice → 10.40.1.40:8096
```

The dedicated gateway accepts only the Jellyfin hostname and routes from `non-cluster-services`. TLS uses `kube-system/wildcard-certificate-tls`. Streaming request timeouts are disabled. The existing internal gateway also serves the hostname, and internal DNS points it to `internal.r1p.io`.

The public A record is **DNS-only** in Cloudflare. Video does not traverse the Cloudflare Tunnel or proxy. The UniFi rule **Jellyfin HTTPS** forwards WAN TCP `443` to `10.50.50.3:443`; NAS port `8096` is not forwarded. Jellyfin's trusted proxies are the six Kubernetes node addresses `10.40.1.200`–`10.40.1.205`, and UPnP is disabled.

The Jellyfin Flux Kustomization supplies `JELLYFIN_WAN_IP` through `spec.postBuild.substitute`. This public DNS address is a separate routing value because the shared `domains-secret` WAN value did not match the router during installation. It contains no credentials.

**The WAN uses DHCP.** When its address changes, update `JELLYFIN_WAN_IP` in [the Jellyfin Kustomization](../kubernetes/apps/non-cluster-services/jellyfin/ks.yaml) to the router's current public IPv4, merge the change, and reconcile Flux Kustomization `jellyfin`. This deployment does not install a dynamic DNS updater. Check public DNS and test from outside the LAN after an address change.

## Deploy, verify, and maintain

1. Validate repository changes with `task validate`.
2. In TrueNAS Apps, install or edit the custom app `jellyfin` using the Compose definition. A copy is kept at `/mnt/zpool/jellyfin/compose.yaml`. Applying repository changes alone does not update the NAS app.
3. Complete the Jellyfin startup wizard and set account passwords before opening the router rule. Configure the libraries, QSV device, network proxy addresses, tuner, and recording path as above. Runtime settings persist in `/config`.
4. Merge the GitOps changes, confirm `jellyfin` and `cilium-gateway` reconcile successfully, and confirm both HTTPRoute parents accept the route.
5. Create or verify the named UniFi rule only after the authenticated service and gateway are ready.
6. Verify `/health` returns `Healthy` over HTTPS, the certificate is valid, unauthenticated library requests are rejected, and authenticated playback works. Also test from outside the home network; LAN hairpin access alone does not prove public reachability.

For maintenance, snapshot `zpool/jellyfin/config` before upgrading the pinned image. Update the Compose image and digest together, apply it through the TrueNAS custom app, and verify playback before removing the snapshot. Cache/transcode datasets are disposable; configuration and recordings need their own backup policy. Existing Kubernetes PVC backups do not cover these NAS datasets.

## Rollback

Disable only the **Jellyfin HTTPS** UniFi port forward to close public access. Stop only the TrueNAS app `jellyfin` if needed. Remove the Jellyfin Flux resources, dedicated gateway, and DNS records through a repository change. Preserve `zpool/jellyfin/config` and recordings if the trial may resume. Do not delete the shared media datasets or modify the existing Plex container, mounts, port forward, or DNS records.
