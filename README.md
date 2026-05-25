# 🚀 3-Tier Application Deployment on AKS using Terraform & Helm

This repository demonstrates how to provision an Azure Kubernetes Service (AKS) cluster using Terraform and deploy a 3-tier application using Helm.

---

# 📌 Architecture Overview

```text
Terraform → Infrastructure Provisioning
  ├── AKS Cluster
  ├── Azure Container Registry (ACR)
  └── Networking

Helm → Application Deployment
  ├── Web Tier (Nginx)
  ├── Backend API (Custom Image)
  ├── Database (MySQL/MariaDB)
  ├── Ingress Controller
  └── Secrets & Configurations
```

---

# 🧰 Prerequisites

Ensure the following tools are installed:

* Azure CLI
* Terraform
* kubectl
* Helm
* Docker

Login to Azure:

```bash
az login
```

---

# 🏗️ Step 1: Provision AKS using Terraform

## 1. Initialize Terraform

```bash
terraform init
```

## 2. Validate configuration

```bash
terraform validate
```

## 3. Apply infrastructure

```bash
terraform apply
```

Confirm with `yes` when prompted.

---

## 4. Get AKS credentials

```bash
az aks get-credentials --resource-group <resource-group> --name <aks-cluster-name>
```

Verify cluster access:

```bash
kubectl get nodes
```

---

# 📦 Step 2: Build & Push Backend Docker Image

👉 Only the backend is a custom image. Web (Nginx) and DB use public images.

## 1. Login to ACR

```bash
az acr login --name <acr-name>
```

## 2. Build backend image

```bash
docker build -t <acr-name>.azurecr.io/myapp-backend:latest ./backend
```

## 3. Push backend image

```bash
docker push <acr-name>.azurecr.io/myapp-backend:latest
```

---

# 🌐 Step 3: Install Ingress Controller

```bash
kubectl create namespace ingress-nginx

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx
```

Check external IP:

```bash
kubectl get svc -n ingress-nginx
```

---

# 🔐 Step 4: Configure Secrets (Helm)

Secrets are managed via Helm templates.

## values.yaml

```yaml
secrets:
  mysqlrootpassword: yourpassword
  djangoPassword: yourpassword
```

## templates/secret.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
stringData:
  DB_USER: {{ .Values.secrets.dbUser }}
  DB_PASSWORD: {{ .Values.secrets.dbPassword }}
```

---

# ⚙️ Step 5: Helm Chart Setup

## Create Helm chart

```bash
helm create 3tier-app
```

Clean default templates:

```bash
rm -rf 3tier-app/templates/*
```

## Add your Kubernetes manifests into:

```text
3tier-app/
  Chart.yaml
  values.yaml
  templates/
    backend.yaml
    web.yaml
    db.yaml
    ingress.yaml
    pvc.yaml
    secret.yaml
```

---

## Use values in templates

Example (backend):

```yaml
image: {{ .Values.backend.image }}
replicas: {{ .Values.backend.replicas }}
```

## values.yaml (important update)

```yaml
backend:
  image: <acr-name>.azurecr.io/myapp-backend:latest
  replicas: 1

web:
  image: nginx:alpine

db:
  image: mariadb:10.6
```

---

# 🚀 Step 6: Deploy Application using Helm

## Install application

```bash
helm install myapp ./3tier-app -n web-tier --create-namespace
```

---

## Upgrade application (after changes)

```bash
helm upgrade myapp ./3tier-app
```

---

## Uninstall application

```bash
helm uninstall myapp
```

---

# 🔍 Step 7: Verification

## Check pods

```bash
kubectl get pods -A
```

## Check services

```bash
kubectl get svc -A
```

## Check ingress

```bash
kubectl get ingress -A
```

---

# 🌍 Step 8: Access Application

1. Get Ingress external IP:

```bash
kubectl get svc -n ingress-nginx
```

2. Update your local `/etc/hosts`:

```bash
<EXTERNAL-IP> myapp.local
```

3. Open in browser:

```text
http://myapp.local
```

---

# 🔁 Redeployment Workflow

Whenever you make changes:

```bash
helm upgrade myapp ./3tier-app
```

If backend image is updated:

```bash
docker build -t <acr-name>.azurecr.io/myapp-backend:latest ./backend
docker push <acr-name>.azurecr.io/myapp-backend:latest
helm upgrade myapp ./3tier-app
```

If secrets/configs changed:

```bash
kubectl rollout restart deployment backend -n web-tier
kubectl rollout restart deployment web -n web-tier
```

---

# ⚠️ Important Notes

* Only backend uses a custom Docker image
* Web (Nginx) and DB use public images
* Do NOT mix `kubectl apply` and Helm for same resources
* Avoid committing secrets to Git
* Ensure ACR is attached to AKS for image pulling

---

# 📈 Future Improvements

* CI/CD pipeline (GitHub Actions / Azure DevOps)
* Azure Key Vault integration for secrets
* TLS via cert-manager
* Autoscaling (HPA)
* Monitoring (Prometheus + Grafana)

---

# ✅ Summary

This setup provides:

* Infrastructure as Code using Terraform
* Helm-based Kubernetes deployments
* Secure secret handling
* Scalable 3-tier architecture on AKS

---

Feel free to fork and enhance 🚀
