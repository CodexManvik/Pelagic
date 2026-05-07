locals {
  required_apis = toset([
    "run.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
  ])
}

resource "google_project_service" "required" {
  for_each = local.required_apis

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_service_account" "runtime" {
  account_id   = "leviathan-backend-runtime"
  display_name = "Project Leviathan Backend Runtime SA"
}

resource "google_project_iam_member" "runtime_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_project_iam_member" "runtime_metrics" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_cloud_run_v2_service" "backend" {
  name     = var.cloud_run_service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.runtime.email

    containers {
      image = var.backend_image

      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }
      env {
        name  = "QSTASH_TOKEN"
        value = var.qstash_token
      }
      env {
        name  = "QSTASH_CURRENT_SIGNING_KEY"
        value = var.qstash_current_signing_key
      }
      env {
        name  = "GROQ_API_KEY"
        value = var.groq_api_key
      }
    }
  }

  depends_on = [google_project_service.required]
}

# Allow QStash and other public callers to reach the webhook endpoint.
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_service_account" "github_actions_deployer" {
  account_id   = "leviathan-gha-deployer"
  display_name = "Project Leviathan GitHub Actions Deployer SA"
}

resource "google_project_iam_member" "gha_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_actions_deployer.email}"
}

resource "google_service_account_iam_member" "gha_runtime_impersonation" {
  service_account_id = google_service_account.runtime.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_actions_deployer.email}"
}

resource "google_iam_workload_identity_pool" "github" {
  provider                  = google-beta
  workload_identity_pool_id = "github-actions-pool"
  display_name              = "GitHub Actions Pool"
  description               = "OIDC identities from GitHub Actions."

  depends_on = [google_project_service.required]
}

resource "google_iam_workload_identity_pool_provider" "github_oidc" {
  provider = google-beta

  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-oidc-provider"
  display_name                       = "GitHub OIDC Provider"
  description                        = "token.actions.githubusercontent.com provider"

  attribute_mapping = {
    "google.subject"           = "assertion.sub"
    "attribute.actor"          = "assertion.actor"
    "attribute.repository"     = "assertion.repository"
    "attribute.repository_ref" = "assertion.ref"
  }

  attribute_condition = "assertion.repository == '${var.github_repository}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "gha_wif_user" {
  service_account_id = google_service_account.github_actions_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
}
