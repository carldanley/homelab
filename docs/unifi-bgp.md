# Using Cilium with UniFi BGP

[UniFi OS 4.1.13](https://community.ui.com/releases/UniFi-OS-Dream-Machines-4-1-13/9a86563f-19aa-4cdb-bccf-41f33721b9e9) introduced official, native support for [FRR](https://frrouting.org/) which implements BGP. With [Cilium](https://cilium.io/), we can make use of BGP to advertise IPs for our Kubernetes Services of `type: LoadBalancer`.

UniFi does publish some [official documentation about BGP](https://help.ui.com/hc/en-us/articles/16271338193559-UniFi-Border-Gateway-Protocol-BGP) but this document serves to add additional context.

## Prerequisites

Before we can advertise routes from Kubernetes (via Cilium), we need to ensure the following:

- We have a healthy Kubernetes cluster with Cilium installed
- We have one of the following switches or gateways:
  - EFG, UDM-Pro-Max, UDM-SE, UDM-Pro, or UDW with UniFi OS version 4.1.13 or newer
  - UXG-Enterprise with firmware version 4.1.8 or newer
  - ECS-Aggregation

## Configuration

### FRR Configuration

To get started, we need to configure FRR on the UniFi switch (or gateway). This will allow Cilium to advertise routes through peering to the UniFi device (and thus, your network). FRR uses a file named `frr.conf` to store the configuration for peering like this:

```
! -*- bgp -*-
!
hostname $UDMP_HOSTNAME
password zebra
frr defaults traditional
log file stdout
!
router bgp 64521
 bgp ebgp-requires-policy
 bgp router-id <YOUR-UNIFI-DEVICE-IP>
 maximum-paths 3
 neighbor cilium peer-group
 neighbor cilium remote-as 64520
 neighbor cilium activate
 neighbor cilium soft-reconfiguration inbound
 neighbor <NODE-1> peer-group cilium
 neighbor <NODE-2> peer-group cilium
 neighbor <NODE-3> peer-group cilium
 address-family ipv4 unicast
  redistribute connected
  neighbor cilium activate
  neighbor cilium route-map ALLOW-ALL in
  neighbor cilium route-map ALLOW-ALL out
  neighbor cilium next-hop-self
 exit-address-family
 !
route-map ALLOW-ALL permit 10
!
line vty
!
```

In the configuration above, be sure to replace the following placeholders:

- `<YOUR-UNIFI-DEVICE-IP>` - This should be the IP address of the UniFi device that Cilium will advertise routes to
- `<NODE-1>` - This should be the IP of the first Kubernetes control plane node in your cluster
- `<NODE-2>` - This should be the IP of the second Kubernetes control plane node in your cluster
- `<NODE-3>` - This should be the IP of the third Kubernetes control plane node in your cluster

Once you've created this file and corrected the placeholders, it's time to upload the configuration to UniFi. To upload the `frr.conf` file to your UniFi device, browse to `Settings` > `Routing` > `BGP` and fill in the form data as necessary.

### Cilium Configuration

Next, it's time to configure Cilium to correctly advertise the routes from Kubernetes. In the `frr.conf` file above, remember that we configured the UniFi device as a BGP peer available at `<YOUR-UNIFI-DEVICE-IP>` (which you changed) using an ASN of `64521`. Using this information, you can create the configuration for Cilium using CRDs, like this:

```yaml
---
apiVersion: cilium.io/v2alpha1
kind: CiliumBGPClusterConfig
metadata:
  name: unifi
spec:
  nodeSelector:
    matchLabels:
      kubernetes.io/os: linux
  bgpInstances:
    - name: "instance-64520"
      localASN: 64520
      peers:
        - name: "peer-64521"
          peerASN: 64521
          peerAddress: <YOUR-UNIFI-DEVICE-IP>
          peerConfigRef:
            name: "cilium-bgp-peer"
---
apiVersion: cilium.io/v2alpha1
kind: CiliumBGPPeerConfig
metadata:
  name: cilium-bgp-peer
spec:
  timers:
    holdTimeSeconds: 9
    keepAliveTimeSeconds: 3
  ebgpMultihop: 4
  gracefulRestart:
    enabled: true
    restartTimeSeconds: 15
  families:
    - afi: ipv4
      safi: unicast
      advertisements:
        matchLabels:
          advertise: "bgp"
---
apiVersion: cilium.io/v2alpha1
kind: CiliumBGPAdvertisement
metadata:
  name: cilium-bgp-advertisements
  labels:
    advertise: bgp
spec:
  advertisements:
    - advertisementType: "Service"
      service:
        addresses:
          - LoadBalancerIP
      selector:
        matchExpressions:
        - {key: somekey, operator: NotIn, values: ['never-used-value']}
---
apiVersion: "cilium.io/v2alpha1"
kind: CiliumLoadBalancerIPPool
metadata:
  name: ip-pool
spec:
  blocks:
    - cidr: <YOUR-KUBERNETES-SERVICES-CIDR>
```

In the configuration above, be sure to replace the following placeholders:

- `<YOUR-UNIFI-DEVICE-IP>` - This should be the IP address of the UniFi device that Cilium will advertise routes to (you configured this in `frr.conf` - be sure it's the same)
- `<YOUR-KUBERNETES-SERVICES-CIDR>` - This will be the CIDR block pool that your `Services` of `type: LoadBalancer` can acquire IP addresses from; it looks something like `192.168.100.1/24`.

Once you've created this file and corrected the placeholders, it's time to apply the configuration to Kubernetes via something like `kubectl apply -f cilium-config.yaml`.

### Verifiying the Configuration

To verify that the routes are being advertised correctly, you can use the following methods:

On the UniFi device, check the BGP neighbors and advertised routes:

```bash
vtysh -c "show ip bgp summary"
vtysh -c "show ip bgp"
```

On the Kubernetes cluster, exec into a Cilium pod and check the BGP status:

```bash
cilium bgp peers
```
