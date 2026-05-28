# Powerwall Dashboard

Powerwall Dashboard runs in cloud mode for Tesla Powerwall 3 monitoring. The deployment uses pyPowerwall for Tesla cloud reads, Telegraf for collection, and the in-cluster Prometheus/Grafana stack for dashboards and Alertmanager notifications.

## Secrets

Create a `powerwall-dashboard` item in 1Password with:

```sh
PW_EMAIL=<tesla-account-email>
```

## First Login

After Flux creates the deployment and PVC, complete the one-time Tesla browser authentication from the pyPowerwall pod:

```sh
kubectl -n selfhosted exec -it deploy/powerwall-dashboard-pypowerwall -- \
  python3 -m pypowerwall setup -headless -authpath /app/.auth
```

Follow the printed Tesla login URL, then paste the callback URL back into the prompt. The generated auth files are stored on the `powerwall-dashboard-auth` PVC.

## Alerts

Prometheus alerts are routed to the default homelab Discord receiver:

- Collector or Tesla cloud telemetry missing/degraded
- Active Powerwall alerts from pyPowerwall
- Utility grid down
- Powerwall below 25% during an outage, which is the Generac prep threshold
- Powerwall below 15% during an outage, which is the critical threshold
