output "cloud_run_service_url" {
  description = "Project Leviathan backend URL. Use this as QStash target base URL."
  value       = google_cloud_run_v2_service.backend.uri
}

output "qstash_destination_url" {
  description = "Full QStash destination URL for ARGO webhook ingestion."
  value       = "${google_cloud_run_v2_service.backend.uri}/api/webhooks/argo-ingest"
}

output "github_actions_service_account_email" {
  description = "Service account email for GitHub Actions deployment."
  value       = google_service_account.github_actions_deployer.email
}

output "github_workload_identity_provider" {
  description = "Workload Identity Provider resource name for GitHub Actions auth."
  value       = google_iam_workload_identity_pool_provider.github_oidc.name
}
