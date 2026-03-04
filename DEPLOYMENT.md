# Frontend Deployment Guide

This guide explains the CI/CD pipeline for deploying the frontend application to AWS EKS.

## Architecture Overview

The deployment pipeline consists of three jobs:
1. **Build**: Compiles the React application and runs tests
2. **Push**: Builds and pushes Docker image to Docker Hub
3. **Deploy**: Deploys the image to AWS EKS cluster

## Prerequisites

### Required GitHub Secrets

Configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

#### Docker Registry Secrets
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password or access token

#### AWS Secrets
- `AWS_ACCESS_KEY_ID`: AWS IAM access key with EKS permissions
- `AWS_SECRET_ACCESS_KEY`: AWS IAM secret access key

### AWS IAM Permissions Required

Your AWS IAM user needs the following permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters",
        "eks:AccessKubernetesApi"
      ],
      "Resource": "*"
    }
  ]
}
```

## Creating AWS EKS Cluster

If you don't have an EKS cluster yet, follow these steps to create one using AWS CLI.

### Prerequisites for Cluster Creation

1. Install AWS CLI:
```bash
# Ubuntu/Debian
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

2. Install eksctl (EKS cluster management tool):
```bash
# Linux
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Verify installation
eksctl version
```

3. Install kubectl:
```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client
```

4. Configure AWS credentials:
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: ap-south-1
# Default output format: json
```

### Create EKS Cluster with One Node

Use the following command to create a simple EKS cluster in ap-south-1 region with one t3.small node:

```bash
eksctl create cluster \
  --name stress-detection-cluster \
  --region ap-south-1 \
  --node-type t3.small \
  --nodes 1 \
  --nodes-min 1 \
  --nodes-max 1 \
  --managed
```

### Cluster Creation Details

- **Cluster Name**: stress-detection-cluster
- **Region**: ap-south-1 (Mumbai)
- **Node Type**: t3.small (2 vCPU, 2 GB RAM)
- **Number of Nodes**: 1
- **Node Group**: Managed (AWS handles node updates)

The cluster creation process takes approximately 15-20 minutes. You'll see output showing the progress.

### Verify Cluster Creation

After creation completes, verify your cluster:

```bash
# List clusters
aws eks list-clusters --region ap-south-1

# Describe cluster
aws eks describe-cluster --name stress-detection-cluster --region ap-south-1

# Update kubeconfig
aws eks update-kubeconfig --region ap-south-1 --name stress-detection-cluster

# Verify kubectl access
kubectl get nodes
kubectl get namespaces
```

### Alternative: Quick Cluster Creation (Minimal Options)

For the simplest setup:

```bash
eksctl create cluster --name stress-detection-cluster --region ap-south-1 --node-type t3.small --nodes 1
```

### Cluster Configuration File (Advanced)

Alternatively, create a cluster using a configuration file for better control:

**cluster-config.yaml**:
```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: stress-detection-cluster
  region: ap-south-1

managedNodeGroups:
  - name: frontend-nodes
    instanceType: t3.small
    desiredCapacity: 1
    minSize: 1
    maxSize: 1
    volumeSize: 20
    labels:
      role: frontend
    tags:
      Environment: production
      Application: stress-detection

iam:
  withOIDC: true
```

Create cluster from config:
```bash
eksctl create cluster -f cluster-config.yaml
```

### View Cluster Information

Check cluster details and status using AWS CLI:

```bash
# List all EKS clusters in the region
aws eks list-clusters --region ap-south-1

# Get detailed cluster information
aws eks describe-cluster --name stress-detection-cluster --region ap-south-1 --query cluster

# Get cluster endpoint
aws eks describe-cluster --name stress-detection-cluster --region ap-south-1 --query "cluster.endpoint" --output text

# Get cluster status
aws eks describe-cluster --name stress-detection-cluster --region ap-south-1 --query "cluster.status" --output text

# Get cluster version
aws eks describe-cluster --name stress-detection-cluster --region ap-south-1 --query "cluster.version" --output text

# List node groups
aws eks list-nodegroups --cluster-name stress-detection-cluster --region ap-south-1

# Describe node group
aws eks describe-nodegroup --cluster-name stress-detection-cluster --nodegroup-name <nodegroup-name> --region ap-south-1

# Get cluster ARN
aws eks describe-cluster --name stress-detection-cluster --region ap-south-1 --query "cluster.arn" --output text

# View cluster in AWS Console
echo "https://ap-south-1.console.aws.amazon.com/eks/home?region=ap-south-1#/clusters/stress-detection-cluster"
```

### View Cluster Resources with kubectl

```bash
# Get all nodes
kubectl get nodes -o wide

# Get node details
kubectl describe nodes

# Get all namespaces
kubectl get namespaces

# Get all resources in default namespace
kubectl get all -n default

# Get cluster info
kubectl cluster-info

# Get cluster version
kubectl version

# View cluster events
kubectl get events --sort-by='.lastTimestamp'
```

### Cleanup and Delete Cluster

When you no longer need the cluster, follow these steps to clean up all resources:

#### Step 1: Delete Kubernetes Resources

```bash
# Delete deployments
kubectl delete deployment frontend-deployment -n default

# Delete services
kubectl delete service frontend-service -n default

# Delete HPA
kubectl delete hpa frontend-hpa -n default

# Delete ConfigMaps
kubectl delete configmap frontend-config -n default

# Or delete everything from deployment file
kubectl delete -f deployment.yaml

# Verify all resources are deleted
kubectl get all -n default
```

#### Step 2: Delete EKS Cluster

```bash
# Delete cluster (this will also delete associated node groups)
eksctl delete cluster --name stress-detection-cluster --region ap-south-1

# Force delete if needed (skip confirmation)
eksctl delete cluster --name stress-detection-cluster --region ap-south-1 --force

# Wait for deletion to complete (can take 10-15 minutes)
```

#### Step 3: Verify Cluster Deletion

```bash
# Confirm cluster is deleted
aws eks list-clusters --region ap-south-1

# Check if cluster still exists
aws eks describe-cluster --name stress-detection-cluster --region ap-south-1 2>&1 || echo "Cluster deleted successfully"
```

#### Step 4: Cleanup Additional AWS Resources (if any)

```bash
# List and delete Load Balancers created by services
aws elb describe-load-balancers --region ap-south-1 --query "LoadBalancerDescriptions[?contains(DNSName, 'stress-detection')]"

# List and delete security groups (if manually created)
aws ec2 describe-security-groups --region ap-south-1 --filters "Name=group-name,Values=*eks*"

# Check for any remaining EBS volumes
aws ec2 describe-volumes --region ap-south-1 --filters "Name=tag:kubernetes.io/cluster/stress-detection-cluster,Values=owned"
```

#### Complete Cleanup Script

```bash
#!/bin/bash

# Complete cleanup script for stress-detection-cluster

echo "Starting cleanup process..."

# Delete Kubernetes resources
echo "Deleting Kubernetes resources..."
kubectl delete -f deployment.yaml 2>/dev/null || echo "Deployment file not found or already deleted"

# Delete cluster
echo "Deleting EKS cluster (this may take 10-15 minutes)..."
eksctl delete cluster --name stress-detection-cluster --region ap-south-1 --wait

# Verify deletion
echo "Verifying cluster deletion..."
if aws eks describe-cluster --name stress-detection-cluster --region ap-south-1 2>&1 | grep -q "ResourceNotFoundException"; then
    echo "✅ Cluster deleted successfully!"
else
    echo "⚠️  Cluster may still be deleting. Check AWS Console."
fi

echo "Cleanup complete!"
```

**⚠️ Warning**: This will permanently delete:
- All pods, deployments, and services
- All persistent volumes and data
- The entire EKS cluster and node groups
- Associated AWS resources (Load Balancers, Security Groups)

**💰 Cost Savings**: Deleting the cluster stops all charges. Estimated savings: ~$30-50/month for a t3.small single-node cluster.

## Configuration

### 1. Update Workflow Variables

Edit `.github/workflows/frontend-deploy.yml` and update these environment variables:

```yaml
env:
  AWS_REGION: ap-south-1                         # Your AWS region (Mumbai)
  EKS_CLUSTER_NAME: stress-detection-cluster     # Your EKS cluster name
  DOCKER_IMAGE_NAME: stress-detection-frontend   # Your Docker image name
  K8S_NAMESPACE: default                         # Kubernetes namespace
```

### 2. Update Deployment Manifest

Edit `deployment.yaml` and replace `<DOCKER_USERNAME>` with your actual Docker Hub username:

```yaml
image: <DOCKER_USERNAME>/stress-detection-frontend:latest
```

## Deployment Files

### Created Files

1. **frontend/Dockerfile**
   - Multi-stage build (Node.js + Nginx)
   - Optimized for production
   - Includes health checks

2. **.github/workflows/frontend-deploy.yml**
   - Triggers only on frontend/ directory changes
   - Three-job pipeline (build → push → deploy)
   - Automated testing and deployment

3. **deployment.yaml** (root directory)
   - Kubernetes Deployment (3 replicas)
   - LoadBalancer Service
   - Horizontal Pod Autoscaler (2-10 pods)
   - ConfigMap for nginx configuration

4. **frontend/.dockerignore**
   - Optimizes Docker build context

## Workflow Trigger

The workflow triggers automatically when you push changes to the `frontend/` directory on `main` or `develop` branches:

```bash
git add frontend/
git commit -m "Update frontend"
git push origin main
```

## Manual Trigger (Optional)

To enable manual workflow runs, add this to the workflow file:

```yaml
on:
  push:
    paths:
      - 'frontend/**'
    branches:
      - main
      - develop
  workflow_dispatch:  # Add this line
```

## Deployment Process

1. **Build Job**:
   - Checks out code
   - Installs Node.js dependencies
   - Runs tests
   - Builds React application
   - Uploads build artifacts

2. **Push Job**:
   - Builds Docker image
   - Tags with branch name and commit SHA
   - Pushes to Docker Hub registry
   - Uses layer caching for faster builds

3. **Deploy Job**:
   - Configures AWS credentials
   - Updates kubeconfig for EKS cluster
   - Updates deployment with new image
   - Applies Kubernetes manifests
   - Waits for rollout completion
   - Verifies deployment

## Kubernetes Resources

### Deployment
- **Replicas**: 3 (can be scaled by HPA)
- **Strategy**: RollingUpdate (zero downtime)
- **Resource Limits**: 256Mi memory, 200m CPU
- **Probes**: Liveness and Readiness checks

### Service
- **Type**: LoadBalancer (exposes external IP)
- **Port**: 80

### HPA (Horizontal Pod Autoscaler)
- **Min Replicas**: 2
- **Max Replicas**: 10
- **Target CPU**: 70%
- **Target Memory**: 80%

## Monitoring Deployment

### Check Workflow Status
Visit: `https://github.com/<username>/<repo>/actions`

### Check Kubernetes Resources

```bash
# Configure kubectl
aws eks update-kubeconfig --region ap-south-1 --name stress-detection-cluster

# Check pods
kubectl get pods -l app=frontend

# Check service
kubectl get service frontend-service

# Check deployment status
kubectl rollout status deployment/frontend-deployment

# View logs
kubectl logs -l app=frontend --tail=100
```

### Get External URL

```bash
kubectl get service frontend-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## Rollback

If you need to rollback to a previous version:

```bash
# View rollout history
kubectl rollout history deployment/frontend-deployment

# Rollback to previous version
kubectl rollout undo deployment/frontend-deployment

# Rollback to specific revision
kubectl rollout undo deployment/frontend-deployment --to-revision=2
```

## Troubleshooting

### Build Fails
- Check Node.js version compatibility
- Verify package.json dependencies
- Review test logs

### Push Fails
- Verify Docker Hub credentials
- Check DOCKER_USERNAME and DOCKER_PASSWORD secrets
- Ensure Docker Hub repository exists

### Deploy Fails
- Verify AWS credentials and permissions
- Check EKS cluster name and region
- Ensure kubectl can access the cluster
- Review pod logs: `kubectl logs -l app=frontend`

### Image Pull Errors
- Ensure image exists in Docker Hub
- Verify image tag in deployment.yaml
- Check if repository is public or add imagePullSecrets

## Security Best Practices

1. Use Docker Hub access tokens instead of passwords
2. Use AWS IAM roles with minimal required permissions
3. Enable AWS CloudTrail for audit logging
4. Use Kubernetes namespaces for isolation
5. Implement network policies if needed
6. Regularly update base images for security patches

## Cost Optimization

1. Adjust HPA min/max replicas based on traffic
2. Use spot instances for EKS worker nodes
3. Implement cluster autoscaler
4. Monitor and optimize resource requests/limits

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
