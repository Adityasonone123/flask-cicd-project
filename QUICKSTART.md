# Quick Start Guide - Flask CI/CD Pipeline

## 🚀 Get Started in 5 Minutes

### Step 1: Install Required Tools (if not already installed)

```powershell
# Install Git
choco install git

# Install Python (if needed)
choco install python

# Install Docker Desktop
choco install docker-desktop

# Install kubectl
choco install kubernetes-cli

# Install Minikube (for local Kubernetes)
choco install minikube
```

### Step 2: Start Your Kubernetes Cluster

**Option A: Using Minikube (Recommended for local testing)**
```powershell
minikube start
minikube tunnel  # Keep this running in a separate terminal
```

**Option B: Using Kind**
```powershell
kind create cluster
```

### Step 3: Verify Setup

Run the setup verification script:
```powershell
python setup.py
```

This will check:
- ✓ All required tools are installed
- ✓ Kubernetes cluster is accessible
- ✓ Tests pass
- ✓ Docker image can be built

### Step 4: Configure GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `DOCKER_USERNAME` | Your DockerHub username |
| `DOCKER_PASSWORD` | Your DockerHub password or access token |
| `KUBECONFIG` | Your kubeconfig file (base64 encoded) |

**How to get KUBECONFIG:**

For Minikube:
```powershell
# PowerShell
$kubeconfig = Get-Content "$HOME\.kube\config" -Raw
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($kubeconfig))
```

Copy the output and paste it as the KUBECONFIG secret value.

### Step 5: Initialize Git and Push

```powershell
# Initialize git (if not already done)
git init
git add .
git commit -m "Setup Flask CI/CD pipeline"

# Set main branch
git branch -M main

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

### Step 6: Watch the Pipeline

1. Go to GitHub repository
2. Click **Actions** tab
3. Click on the workflow run
4. Watch each stage execute:
   - ✅ Test
   - ✅ Build & Push
   - ✅ Deploy

### Step 7: Access Your Application

**For Minikube:**
```powershell
minikube service flask-service -n flask-app
```

**For Kind or Cloud:**
```powershell
kubectl get services -n flask-app
# Access via the EXTERNAL-IP shown
```

---

## 📋 Checklist

Before pushing code, ensure:

- [ ] Docker Desktop is running
- [ ] Kubernetes cluster is running (`kubectl cluster-info`)
- [ ] GitHub secrets are configured
- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] You have a DockerHub account and repository

---

## 🔍 Troubleshooting

### Issue: Pipeline fails at Docker login
**Solution:** Verify DOCKER_USERNAME and DOCKER_PASSWORD in GitHub Secrets

### Issue: Deployment stuck in Pending state
**Solution:** 
- For Minikube: Ensure `minikube tunnel` is running
- Check resources: `kubectl describe nodes`

### Issue: Cannot access application
**Solution:**
- Minikube: Use `minikube service flask-service -n flask-app`
- Check pods: `kubectl get pods -n flask-app`
- View logs: `kubectl logs -l app=flask-app -n flask-app`

### Issue: Tests fail in pipeline
**Solution:** Run tests locally first: `pytest tests/ -v`

---

## 🎯 What Happens When You Push Code?

```
Push to main branch
        ↓
┌───────────────────┐
│  1. TEST STAGE    │ ← Runs on every push/PR
│  - Checkout code  │
│  - Install deps   │
│  - Run pytest     │
│  - Coverage report│
└─────────┬─────────┘
          ↓
┌───────────────────┐
│  2. BUILD STAGE   │ ← Only on main branch
│  - Login DockerHub│
│  - Build image    │
│  - Tag with SHA   │
│  - Push to registry│
└─────────┬─────────┘
          ↓
┌───────────────────┐
│  3. DEPLOY STAGE  │ ← Only on main branch
│  - Configure kubectl│
│  - Update manifests│
│  - Apply to K8s   │
│  - Wait rollout   │
│  - Verify deploy  │
└─────────┬─────────┘
          ↓
    ✅ Live!
```

---

## 📊 Pipeline Status

The pipeline triggers on:
- **Push to main**: Runs all stages (Test → Build → Deploy)
- **Pull Request**: Runs only Test stage

---

## 🎨 Customize

### Change Replica Count
Edit `k8s/deployment.yaml`:
```yaml
spec:
  replicas: 5  # Default is 3
```

### Change Port
Edit `app.py` and `k8s/service.yaml`

### Add Environment Variables
Edit `k8s/deployment.yaml`:
```yaml
env:
- name: FLASK_ENV
  value: "production"
```

---

## 🧪 Test Locally

```powershell
# Run tests
pytest tests/ -v

# Build Docker image
docker build -t flask-cicd-app .

# Run container
docker run -p 5000:5000 flask-cicd-app

# Deploy to Kubernetes manually
kubectl apply -f k8s/
```

---

## 📚 Learn More

Check the full [README.md](README.md) for:
- Detailed architecture explanation
- Advanced configuration options
- Security best practices
- Cost optimization tips
- Monitoring and logging setup

---

**Need Help?** Run `python setup.py` for automated verification!
