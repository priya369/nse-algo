variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Cloud Run region"
  type        = string
  default     = "asia-south1"
}

variable "bigquery_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "asia-south1"
}

variable "container_image" {
  description = "Cloud Run container image"
  type        = string
}

variable "cloud_run_service_account" {
  description = "Cloud Run Job service account"
  type        = string
}