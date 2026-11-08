# AI Log Analyzer Agent
[![CI](https://github.com/varunrajaramrao-glitch/github-ai-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/varunrajaramrao-glitch/github-ai-agents/actions/workflows/ci.yml)

An AI-powered incident-response service that reads raw production error logs and returns a precise, actionable resolution report, using a multi-agent architecture. Containerized with Docker and deployed two ways — to AWS (Terraform + CI/CD) and to Kubernetes.

## The Problem It Solves

Production support engineers lose hours manually reading error logs, searching for generic answers, and piecing together fixes. This service automates that: send it a log, get back context-aware root-cause analysis and concrete resolution steps.

## How It Works

Send error-log content to the `POST /analyze` endpoint. Three specialized agents process it sequentially:

- **Log Analyzer** — reads and summarizes the errors, warnings, and severity
- **Issue Investigator** — performs root-cause analysis and identifies error patterns
- **Solution Specialist** — produces immediate fixes, short-term workarounds, and long-term preventive measures

The response is a structured incident-resolution report.

## Tech Stack

| Area | Tools |
|------|-------|
| Multi-agent orchestration | CrewAI |
| API layer | FastAPI |
| Containerization | Docker |
| Orchestration | Kubernetes (Deployment, Service, Ingress, Secrets, health probes) |
| Infrastructure as Code | Terraform |
| CI/CD | GitHub Actions |
| Cloud | AWS (EC2, IAM, SSM Parameter Store, S3 + DynamoDB remote state) |
| Language | Python |

## Architecture

```
Error Log
   │
   ▼
FastAPI  /analyze
   │
   ▼
CrewAI pipeline (sequential)
   Log Analyzer ─► Issue Investigator ─► Solution Specialist
   │
   ▼
Incident Resolution Report
```

## Deployment

This service has been deployed in two environments.

**AWS (cloud) — since decommissioned.** The container was deployed to AWS EC2 on infrastructure provisioned as code with **Terraform** (IAM roles and instance profile, security groups, and SSM Parameter Store for encrypted secrets, with remote state in S3 and DynamoDB state locking). A **GitHub Actions** pipeline built and pushed the image, then redeployed to the instance via AWS SSM Run Command on each commit — no SSH, secrets pulled from SSM at deploy time. The AWS environment has since been torn down to avoid ongoing cost, so the cloud endpoint is no longer reachable.

**Kubernetes (local, kind).** The same image runs on Kubernetes, defined declaratively in [`log-analyzer-k8s/`](./log-analyzer-k8s):

- **Deployment** with resource requests/limits and **startup, readiness, and liveness probes** against a dependency-free `/health` endpoint
- **Service** (ClusterIP) fronting the pods
- **Ingress** (nginx) for host-based routing, with a raised proxy timeout for the long-running `/analyze` call
- API keys injected via a **Kubernetes Secret**, never baked into the image

> The Terraform IaC is included in this repo:
- **`log-analyzer-infra/`** — AWS EC2 deployment (IAM, security groups, SSM Parameter Store, S3 + DynamoDB remote state)
- **`log-analyzer-eks/`** — Amazon EKS cluster (VPC and managed node groups via community Terraform modules)

## Run Locally with Docker

```bash
docker pull zxcrty/log-analyzer:v2

docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your-gemini-key" \
  -e SERPER_API_KEY="your-serper-key" \
  zxcrty/log-analyzer:v2
```

Then open `http://localhost:8000/docs`.

## Run on Kubernetes

With a running cluster (e.g. [kind](https://kind.sigs.k8s.io/) or minikube) and the nginx ingress controller enabled:

```bash
# create the secret with your API keys (never commit these)
kubectl create secret generic log-analyzer-secrets \
  --from-literal=GEMINI_API_KEY="your-gemini-key" \
  --from-literal=SERPER_API_KEY="your-serper-key"

# apply the manifests
kubectl apply -f log-analyzer-k8s/

# check it comes up
kubectl get pods
kubectl get ingress
```

## API Usage

**Endpoint:** `POST /analyze`

**Request**
```json
{ "log_content": "ERROR: Connection timeout to OrderService at 03:45:22" }
```

**Response**
```json
{ "report": "Incident resolution guide with immediate, short-term and long-term fixes..." }
```

## Screenshots

**API running on AWS EC2 (Swagger UI)**

<img width="700" alt="API documentation" src="https://github.com/user-attachments/assets/28bac1cc-82e4-4dc8-b3e5-967a5ed8bd30" />

**Sample incident-resolution response**

<img width="700" alt="Sample response" src="https://github.com/user-attachments/assets/de02b394-a3fa-44b3-9363-547174390ab6" />

## Future Enhancements

- Asynchronous job model (`202 Accepted` + polling) so long analyses don't hold an HTTP connection open
- File upload for bulk log analysis
- Slack / email notification integration
- Authentication and rate limiting