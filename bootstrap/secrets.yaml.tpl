---
apiVersion: v1
kind: Namespace
metadata:
  name: external-secrets
---
apiVersion: v1
kind: Secret
metadata:
  name: onepassword-secret
  namespace: external-secrets
stringData:
  # for more info on this, check: https://external-secrets.io/latest/provider/1password-automation/
  1password-credentials.json: op://homelab kubernetes/1password-connect-server/1password-credentials.json
  token: op://homelab kubernetes/1password-connect-server/access-token
