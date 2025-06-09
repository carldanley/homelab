# Configuring DNS on UDM-Pro for Ad Blocking

For the longest time, I would set the DNS server on each network to the IP address of Adguard Home (or any other ad-blocking service you choose) and things worked well... until you decide to take down your ad-blocking service for maintenance. You could always set additional servers but I don't want traffic going anywhere else but AdGuard Home (or what's the point?).

Luckily, UniFi lets you set the DNS Server on your WAN for outgoing traffic that isn't directly resolved by your UDM Pro. Now, you can continue to let your UDM Pro automatically handout its own IP for the DNS Server (which you can use for internal domains) and all traffic not resolved by UniFi is then forwarded to the DNS server configured on the WAN (which, in this case, is your ad-blocking service).

The only downside to this is that you lose track of specifically which domains where requested by which IPs (because all requests are forwarded by the UDM Pro). If this is problematic for you, you'll most likely need to change the DNS Server for each network so you can capture this information accordingly.

The upsides are that you can set the primary DNS server on the WAN to your ad blocking service and the secondary to whatever you want your backup DNS server to be. Then, you can run the following command directly on your UDM Pro to force strict-ordering to DNS resolution:

```sh
sed -i 's/all-servers/strict-order/g' /var/run/dnsmasq.conf.d/dns.conf
```

Be sure to restart dnsmasq after making this change with:

```sh
kill $(cat /var/run/dnsmasq.pid)
```

Configuring things to work this way should let you effectively perform maintenance on your ad blocking service and not prevent the network from functioning when the ad blocking service goes offline (since it will failover to your secondary WAN DNS server).
