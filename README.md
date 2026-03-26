# Flask CI/CD Pipeline with Kubernetes

This project demonstrates a complete CI/CD pipeline using GitHub Actions for automated building, testing, and deployment of a Flask application to Kubernetes.

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│   GitHub    │───▶│  GitHub      │───▶│   DockerHub     │───▶│  Kubernetes  │
│   Code      │    │  Actions     │    │   Registry      │    │  Cluster     │
└─────────────┘    └──────────────┘    └─────────────────┘    └──────────────┘
     │                    │                     │                      │
     │                    │                     │                      │
  Push Code          Run Tests            Store Image           Deploy App
  Trigger CI         Build Image          Tag Version           Scale & Run
```

## Pipeline Stages

### 1. **Test Stage** (Automated on every push/PR)
- Checkout code
- Set up Python environment
- Install dependencies
- Run unit tests with pytest
- Upload code coverage report

### 2. **Build & Push Stage** (Only on main branch push)
- Login to DockerHub
- Build Docker image with commit SHA tag
- Tag as latest
- Push to DockerHub registry

### 3. **Deploy Stage** (Only on main branch push)
- Configure kubectl
- Apply Kubernetes namespace
- Update deployment manifest with new image tag
- Apply all Kubernetes manifests
- Wait for rollout completion
- Verify deployment status

## Prerequisites

### 1. GitHub Account
- Create a GitHub account if you don't have one

### 2. DockerHub Account
- Sign up at https://hub.docker.com/
- Create a repository named `flask-cicd-app`

### 3. Kubernetes Cluster
You need a Kubernetes cluster. Options:

#### Option A: Minikube (Local Development)
```bash
# Install Minikube
choco install minikube

# Start cluster
minikube start

# Enable LoadBalancer
minikube tunnel
```

#### Option B: Kind (Kubernetes in Docker)
```bash
# Install Kind
choco install kind

# Create cluster
kind create cluster

# Get kubeconfig
kind get kubeconfig > kubeconfig.txt
```

#### Option C: Cloud Providers
- **AWS EKS**: https://aws.amazon.com/eks/
- **Google GKE**: https://cloud.google.com/kubernetes-engine
- **Azure AKS**: https://azure.microsoft.com/en-us/services/kubernetes-service/

### 4. Install kubectl
```bash
choco install kubernetes-cli
```

## Setup Instructions

### Step 1: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

1. **DOCKER_USERNAME**: Your DockerHub username
2. **DOCKER_PASSWORD**: Your DockerHub password or access token
3. **KUBECONFIG**: Your Kubernetes config file (base64 encoded)

To get KUBECONFIG:

**For Minikube:**
```bash
# The kubeconfig is usually at ~/.kube/config
# Copy the entire file content and encode it:
cat ~/.kube/config | base64 -w 0
```

**For Kind:**
```bash
kind get kubeconfig --name kind | base64 -w 0
```

**For Cloud Providers:**
Download the kubeconfig from your cloud provider's console and encode it.

### Step 2: Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit with CI/CD pipeline"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

### Step 3: Set Up Kubernetes Cluster

#### Using Minikube:
```bash
# Start Minikube
minikube start

# Verify cluster is running
kubectl cluster-info

# Test kubectl connection
kubectl get nodes
```

#### Using Kind:
```bash
# Create cluster
kind create cluster

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### Step 4: Trigger the Pipeline

Push code to the main branch:
```bash
git add .
git commit -m "Trigger CI/CD pipeline"
git push origin main
```

### Step 5: Monitor the Pipeline

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. Select the workflow run
4. Watch each job execute in real-time

### Step 6: Access the Deployed Application

#### For Minikube:
```bash
# Get service URL
minikube service flask-service -n flask-app

# Or get the URL manually
minikube service list
```

#### For Kind or Cloud:
```bash
# Get external IP
kubectl get services -n flask-app

# Access via the EXTERNAL-IP shown
curl http://<EXTERNAL-IP>
```

## Project Structure

```
flask-cicd-project/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions workflow
├── k8s/
│   ├── namespace.yaml         # Kubernetes namespace
│   ├── deployment.yaml        # Deployment configuration
│   └── service.yaml           # Service exposure
├── tests/
│   └── test_app.py            # Unit tests
├── .dockerignore              # Docker ignore rules
├── app.py                     # Flask application
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Kubernetes Resources Explained

### Namespace (`k8s/namespace.yaml`)
- Creates an isolated environment named `flask-app`
- Helps organize and separate resources

### Deployment (`k8s/deployment.yaml`)
- Runs 3 replicas of your Flask app
- Automatically updates pods when new image is pushed
- Includes health checks (liveness and readiness probes)
- Resource limits prevent resource exhaustion

### Service (`k8s/service.yaml`)
- Exposes the application externally
- Type: LoadBalancer
- Routes traffic to pods on port 80 → 5000

## Manual Testing

### Run Locally:
```bash
python app.py
# Access: http://localhost:5000
```

### Run Tests Locally:
```bash
pip install -r requirements.txt
pytest tests/ -v
```

### Build Docker Image Locally:
```bash
docker build -t flask-cicd-app .
docker run -p 5000:5000 flask-cicd-app
```

### Deploy to Kubernetes Manually:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Troubleshooting

### Pipeline Fails at Docker Login
- Verify DOCKER_USERNAME and DOCKER_PASSWORD secrets
- Use DockerHub access token instead of password for better security

### Deployment Stuck in Pending
- Check if cluster has enough resources: `kubectl describe nodes`
- For Minikube, ensure tunnel is running: `minikube tunnel`

### Tests Fail
- Check test output in GitHub Actions logs
- Run tests locally: `pytest tests/ -v`

### Cannot Access Service
- Check service type: `kubectl get services -n flask-app`
- For LoadBalancer, ensure cloud provider supports it
- For Minikube, use: `minikube service flask-service -n flask-app`

### View Logs
```bash
# View pod logs
kubectl logs -l app=flask-app -n flask-app

# Follow logs in real-time
kubectl logs -f -l app=flask-app -n flask-app
```

## Advanced Configuration

### Update Replicas
Edit `k8s/deployment.yaml`:
```yaml
spec:
  replicas: 5  # Change replica count
```

### Add Environment Variables
Edit `k8s/deployment.yaml`:
```yaml
env:
- name: FLASK_ENV
  value: "production"
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: flask-secret
      key: secret-key
```

### Enable Horizontal Pod Autoscaler
Create `k8s/hpa.yaml`:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: flask-hpa
  namespace: flask-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flask-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Security Best Practices

1. **Use DockerHub Access Tokens** instead of passwords
2. **Store secrets in GitHub Secrets**, never in code
3. **Use Kubernetes Secrets** for sensitive data
4. **Enable branch protection** on main branch
5. **Require PR reviews** before merging
6. **Scan images for vulnerabilities** using tools like Trivy

## Cost Optimization

1. **Set resource limits** in deployment.yaml
2. **Use appropriate replica count** for your needs
3. **Enable cluster autoscaling** if using cloud providers
4. **Clean up old deployments** and unused resources

## Next Steps

- Add integration tests
- Implement blue-green deployment strategy
- Add monitoring with Prometheus and Grafana
- Set up logging with ELK stack
- Configure ingress controller for custom domains
- Add database migrations to pipeline

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this project for learning and production.
