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

variable "datasets" {
  description = "BigQuery datasets to create"

  type = map(object({
    location = string
  }))
}

variable "tables" {
  description = "BigQuery tables to create"

  type = map(object({
    dataset_id = string

    schema = list(object({
      name = string
      type = string
      mode = optional(string, "NULLABLE")
    }))

    partition_field     = optional(string)
    clustering          = optional(list(string), [])
    deletion_protection = optional(bool, true)
  }))
}