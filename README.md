Production-Grade 3-Tier Hardened Stack with GitOps & eBPF Observability

This repository contains the declarative configuration for a secure, highly-available 3-tier architecture deployed on Kubernetes (minikube). The project showcases real-world cloud-native engineering practices, emphasizing GitOps delivery workflows, kernel-level eBPF network isolation, and full-stack application monitoring.

    [ Public Ingress / NodePort: 32080 ]
                    │
                    ▼
          ┌───────────────────┐
          │    web-tier       │
          │  Nginx Frontend  │
          └─────────┬─────────┘
                    │  (eBPF Restricted Port 8000)
                    ▼
          ┌───────────────────┐
          │    web-tier       │
          │   Django API      │───[ Scraped via port 8000/metrics ]───┐
          └─────────┬─────────┘                                       │
                    │  (eBPF Restricted Port 3306)                    ▼
                    ▼                                       ┌───────────────────┐
          ┌───────────────────┐                             │  monitoring-tier  │
          │    data-tier      │                             │ Prometheus &      │
          │  MariaDB Database │                             │ Grafana (32300)   │
          └───────────────────┘                             └───────────────────┘

🚀 Key Features

    GitOps Continuous Delivery: Managed entirely via Argo CD, ensuring that the state of the cluster matches this Git repository instantly and automatically heals from configuration drift.

    eBPF-Powered Zero-Trust Security: Utilizes Cilium Network Policies (CiliumNetworkPolicy) interacting directly with the Linux kernel via eBPF. All traffic is blocked by default (default-deny-all), explicitly allowing only strict point-to-point pathways (Frontend ➔ Backend ➔ DB).

    Deep Application Observability: Custom runtime monitoring using Prometheus to pull code-level performance metrics directly from the Django application layer using django-prometheus.

    Visual Command Center: Automated provisioning of Grafana with a declarative Prometheus data source pre-configured to surface traffic metrics, error rates, database latencies, and system health.

    Hardened Configurations: Pods operate under strict non-root security contexts (runAsNonRoot: true), resource quotas limits to mitigate DoS threats, and init-containers to manage database boot dependencies cleanly.

📂 Repository Structure
Plaintext

├── backend.yaml       # Django API Deployment, Service, & Resource Quotas
├── db.yaml            # MariaDB State deployment with Persistent Volume Claims
├── web.yaml           # Nginx Reverse Proxy Deployment & ConfigMap mapping
├── ingress.yaml       # Cilium L3/L4 Network Isolation Policies
├── prometheus.yaml    # Prometheus Scraping Engines & Monitoring Config
└── grafana.yaml       # Grafana Dashboard Provisioning & Auto-Datasource linking

🛠️ Prerequisites

Before executing the deployment, ensure your local workstation is equipped with the following toolchain:

    Linux Engine: Ubuntu 20.04 LTS / 22.04 LTS or newer

    Hypervisor: Minikube (configured with docker/kvm2 driver)

    Kubernetes Orchestrator: kubectl CLI installed matching cluster control-plane version

    Version Control: git for tracking state and triggers

🔧 Installation & Deployment Guide
1. Initialize Local Cluster with Cilium CNI

Spin up a local node bypass mechanism and explicitly disable default basic networking configurations to let Cilium manage the cluster via eBPF kernel hooks:
Bash

minikube start --network-plugin=cni --cni=cilium --memory=4096 --cpus=4

Verify that the eBPF control plane is fully integrated:
Bash

kubectl get pods -n kube-system -l k8s-app=cilium

2. Bootstrap Argo CD (GitOps Controller)

Deploy the GitOps agent engine into a dedicated management workspace namespace:
Bash

kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

To fetch your auto-generated initial dashboard admin password, extract and base64-decode the core secret:
Bash

kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo

3. Build & Load the Backend Image (Minikube Local Registry)

When developing locally, Minikube uses an isolated Docker registry. To ensure your cluster pulls the correct local image without attempting to reach the public internet (which results in ErrImagePull), follow this strict build and tag workflow:

    Point your terminal to Minikube's internal Docker engine:
    Bash

    eval $(minikube docker-env)

    Build and tag the backend image (always bump the version tag to force Kubernetes to recognize the new code):
    Bash

    docker build -t myapp-backend:v2 ./backend

    Update the GitOps manifest: Modify your backend.yaml to reference the new tag and instruct Kubernetes to trust the local cache.
    YAML

    # Inside backend.yaml
    containers:
      - name: backend
        image: myapp-backend:v2       # <--- Ensure this matches your new tag
        imagePullPolicy: IfNotPresent # <--- Prevents calling out to Docker Hub

4. Sync the Infrastructure

Commit the updated manifests and register this repository within your Argo CD application dashboard. Once hooked, Argo CD will provision your workloads across your custom environments (web-tier, data-tier, and monitoring).
📊 Observability & Telemetry Verification
1. Direct Metric Pipeline Testing

Verify the backend container's structural ability to collect code performance statistics directly on port 8000/metrics by querying it internally from the running pod:
Bash

kubectl exec -it deploy/backend -n web-tier -- sh -c "wget -S -O- http://localhost:8000/metrics"

A successful connection bypass returns an HTTP 200 OK followed by rich exposition formats containing telemetry variables such as django_http_requests_total_by_method.
2. Launching Visual Dashboards

Access the pre-provisioned Grafana cluster visualizer exposed via NodePort configuration:

    Retrieve your active cluster URL endpoint:
    Bash

    minikube service grafana -n monitoring --url

    Open the URL in your browser and use the default credentials: Username: admin / Password: admin.

    To view real-time metrics, navigate to the Dashboard management window and import Community ID 17658 to automatically load the target visualizations for your application stack.

🔒 Security Posture & Hardening Verification

To validate your zero-trust architecture, you can test the explicit path-blocking enforced by Cilium's kernel-level eBPF firewalls.

Attempting to run an unauthenticated database connection request directly from a frontend Nginx pod to the database will be instantly dropped at the kernel layer, bypassing standard iptables latency overloads:
Bash

# This connection attempt will hang and timeout due to the zero-trust Cilium policies
kubectl exec -it deploy/web -n web-tier -- nc -zv db.data-tier.svc.cluster.local 3306