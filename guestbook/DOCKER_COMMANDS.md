# Guestbook Docker Build and Push

Use these commands to build and push the guestbook image.

```bash
# Set your namespace once per shell
export MY_NAMESPACE="sn-labs-<your-namespace>"

# Build the image (from repo root)
docker build -t us.icr.io/$MY_NAMESPACE/guestbook:v3 guestbook/v1/guestbook

# Push to IBM Container Registry
docker push us.icr.io/$MY_NAMESPACE/guestbook:v3
```
