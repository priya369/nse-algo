variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
}

variable "table_id" {
  description = "BigQuery table ID"
  type        = string
}

variable "schema" {
  description = "BigQuery table schema"

  type = list(object({
    name = string
    type = string
    mode = optional(string, "NULLABLE")
  }))
}

variable "partition_field" {
  description = "Column used for time partitioning"
  type        = string
  default     = null
}

variable "clustering" {
  description = "Columns used for clustering"
  type        = list(string)
  default     = []
}

variable "deletion_protection" {
  description = "Protect table from accidental deletion"
  type        = bool
  default     = true
}