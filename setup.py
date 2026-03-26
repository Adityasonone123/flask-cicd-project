#!/usr/bin/env python3
"""
Setup script for Flask CI/CD Pipeline
This script helps you set up and verify your Kubernetes cluster
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_prerequisite(name, install_command, check_command):
    """Check if a prerequisite is installed"""
    print(f"Checking {name}...", end=" ")
    success, stdout, stderr = run_command(check_command)
    if success:
        print("✓ Installed")
        return True
    else:
        print("✗ Not found")
        print(f"  Install with: {install_command}")
        return False

def check_kubernetes_cluster():
    """Check if Kubernetes cluster is accessible"""
    print("\nChecking Kubernetes cluster connectivity...")
    success, stdout, stderr = run_command("kubectl cluster-info")
    if success:
        print("✓ Kubernetes cluster is accessible")
        print(f"  {stdout.strip().split(chr(10))[0]}")
        return True
    else:
        print("✗ Cannot connect to Kubernetes cluster")
        return False

def check_kubectl_config():
    """Check if kubectl is configured"""
    print("\nChecking kubectl configuration...")
    success, stdout, stderr = run_command("kubectl config current-context")
    if success:
        print(f"✓ Current context: {stdout.strip()}")
        return True
    else:
        print("✗ kubectl not configured")
        return False

def test_docker_connection():
    """Test Docker connection"""
    print("\nTesting Docker connection...")
    success, stdout, stderr = run_command("docker --version")
    if success:
        print(f"✓ Docker installed: {stdout.strip()}")
        return True
    else:
        print("✗ Docker not found")
        return False

def verify_k8s_manifests():
    """Verify Kubernetes manifests exist"""
    print("\nVerifying Kubernetes manifests...")
    required_files = [
        "k8s/namespace.yaml",
        "k8s/deployment.yaml",
        "k8s/service.yaml"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} not found")
            all_exist = False
    
    return all_exist

def run_tests():
    """Run the test suite"""
    print("\nRunning tests...")
    success, stdout, stderr = run_command("python -m pytest tests/ -v")
    if success:
        print("✓ All tests passed")
        return True
    else:
        print("✗ Some tests failed")
        print(stderr)
        return False

def build_docker_image():
    """Build Docker image locally"""
    print("\nBuilding Docker image...")
    success, stdout, stderr = run_command("docker build -t flask-cicd-app:local .")
    if success:
        print("✓ Docker image built successfully")
        return True
    else:
        print("✗ Failed to build Docker image")
        print(stderr)
        return False

def main():
    print("=" * 60)
    print("Flask CI/CD Pipeline Setup Verification")
    print("=" * 60)
    
    checks_passed = 0
    total_checks = 0
    
    # Check prerequisites
    print("\n--- Checking Prerequisites ---\n")
    
    total_checks += 1
    if check_prerequisite(
        "Python", 
        "Download from python.org", 
        "python --version"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_prerequisite(
        "Git", 
        "choco install git", 
        "git --version"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_prerequisite(
        "Docker", 
        "Install Docker Desktop", 
        "docker --version"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_prerequisite(
        "kubectl", 
        "choco install kubernetes-cli", 
        "kubectl version --client"
    ):
        checks_passed += 1
    
    # Check Docker connection
    total_checks += 1
    if test_docker_connection():
        checks_passed += 1
    
    # Check Kubernetes
    print("\n--- Checking Kubernetes Configuration ---\n")
    
    total_checks += 1
    if check_kubectl_config():
        checks_passed += 1
    
    total_checks += 1
    if check_kubernetes_cluster():
        checks_passed += 1
    
    # Verify manifests
    total_checks += 1
    if verify_k8s_manifests():
        checks_passed += 1
    
    # Run tests
    print("\n--- Running Tests ---\n")
    total_checks += 1
    if run_tests():
        checks_passed += 1
    
    # Build Docker image (optional)
    print("\n--- Optional: Build Docker Image ---\n")
    print("Skip this step if you don't have Docker running")
    response = input("\nBuild Docker image locally? (y/n): ").lower()
    if response == 'y':
        total_checks += 1
        if build_docker_image():
            checks_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Setup Verification Complete: {checks_passed}/{total_checks} checks passed")
    print("=" * 60)
    
    if checks_passed == total_checks:
        print("\n✓ All checks passed! Your environment is ready.")
        print("\nNext steps:")
        print("1. Configure GitHub Secrets (DOCKER_USERNAME, DOCKER_PASSWORD, KUBECONFIG)")
        print("2. Push code to GitHub to trigger the pipeline")
        print("3. Monitor the pipeline in GitHub Actions tab")
        print("4. Access your deployed application using:")
        print("   - Minikube: minikube service flask-service -n flask-app")
        print("   - Cloud: kubectl get services -n flask-app")
    else:
        print("\n⚠ Some checks failed. Please review the output above.")
        print("\nCommon issues:")
        print("- Install missing tools using the suggested commands")
        print("- For Kubernetes, start Minikube: minikube start")
        print("- Or create Kind cluster: kind create cluster")
        print("- Ensure Docker Desktop is running")
    
    return 0 if checks_passed == total_checks else 1

if __name__ == "__main__":
    sys.exit(main())
