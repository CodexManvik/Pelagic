# Project Leviathan Infra (Terraform)

This directory provisions:
- Cloud Run service for the FastAPI backend.
- Runtime and deployment service accounts.
- GitHub Actions Workload Identity Federation (OIDC) for secure deploys.
- Required environment variables on Cloud Run from `terraform.tfvars`.

## Prerequisites

- Terraform `>= 1.6.0`
- GCP project with billing enabled
- `gcloud auth application-default login` or equivalent credentials

## Files

- `versions.tf`: Terraform and provider versions.
- `backend.tf`: local state now, scaffold comment for future GCS backend.
- `providers.tf`: Google providers config.
- `variables.tf`: typed input variables.
- `main.tf`: all resources.
- `outputs.tf`: deployment outputs including Cloud Run URL.
- `terraform.tfvars.example`: sample values.

## Usage

1. Create `terraform.tfvars` from the example and fill real values.
2. Run:
   - `terraform init`
   - `terraform plan`
   - `terraform apply`

## Important Output

- `cloud_run_service_url`: use this as QStash destination base URL.
  - For this project, the webhook target will be:
    - `${cloud_run_service_url}/api/webhooks/argo-ingest`

## GitHub Actions OIDC Inputs

After apply, configure these in your GitHub workflow:
- `workload_identity_provider`: output `github_workload_identity_provider`
- `service_account`: output `github_actions_service_account_email`
