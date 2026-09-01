variable "job_name" {
  description = "Cloud Run Job name"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "image" {
  description = "Container image URI"
  type        = string
}

variable "service_account" {
  description = "Service account used by Cloud Run Job"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for the Cloud Run Job"
  type        = map(string)
  default     = {}
}

variable "cpu" {
  description = "CPU allocated to the Cloud Run Job"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory allocated to the Cloud Run Job"
  type        = string
  default     = "512Mi"
}

variable "timeout" {
  description = "Maximum execution time"
  type        = string
  default     = "3600s"
}

variable "max_retries" {
  description = "Maximum retries for failed tasks"
  type        = number
  default     = 3
}