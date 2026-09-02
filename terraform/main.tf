terraform {
  backend "gcs" {
    bucket = "YOUR-TERRAFORM-STATE-BUCKET"
    prefix = "stock-market"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }

  required_version = ">= 1.5.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
}


# =========================
# BigQuery Datasets
# =========================

resource "google_bigquery_dataset" "datasets" {
  for_each = var.datasets

  project    = var.project_id
  dataset_id = each.key
  location   = each.value.location
}


# =========================
# BigQuery Tables
# =========================

module "bigquery_tables" {
  for_each = var.tables

  source = "./modules/bigquery-table"

  project_id = var.project_id
  dataset_id = each.value.dataset_id
  table_id   = each.key

  schema          = each.value.schema
  partition_field = try(each.value.partition_field, null)
  clustering      = each.value.clustering

  deletion_protection = each.value.deletion_protection

  depends_on = [
    google_bigquery_dataset.datasets
  ]
}

module "nse_ingestion_job" {
  source = "./modules/cloud-run-job"

  job_name = "nse-raw-ingestion"

  region = var.region

  image = var.container_image

  service_account = var.cloud_run_service_account

  environment_variables = {
    GCP_PROJECT_ID = var.project_id
    BQ_DATASET     = "nse_algo"
    BQ_TABLE       = "daily_ohlcv"

    SYMBOL    = "KFINTECH"
    FROM_DATE = "01-01-2023"
    TO_DATE   = "31-08-2026"
  }

  cpu     = "1"
  memory  = "2Gi"
  timeout = "3600s"

  max_retries = 3
}
