variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run."
  type        = string
  default     = "us-central1"
}

variable "cloud_run_service_name" {
  description = "Cloud Run service name for the FastAPI backend."
  type        = string
  default     = "leviathan-backend"
}

variable "backend_image" {
  description = "Container image reference for backend deployment."
  type        = string
}

variable "github_repository" {
  description = "GitHub repository in owner/repo format allowed to deploy."
  type        = string
}

variable "database_url" {
  description = "Neon Postgres connection string."
  type        = string
  sensitive   = true
}

variable "qstash_token" {
  description = "Upstash QStash token."
  type        = string
  sensitive   = true
}

variable "qstash_current_signing_key" {
  description = "Current QStash webhook signing key."
  type        = string
  sensitive   = true
}

variable "groq_api_key" {
  description = "Groq API key."
  type        = string
  sensitive   = true
}
