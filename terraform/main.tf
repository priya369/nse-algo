terraform {
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


resource "google_bigquery_dataset" "stock_market" {
  project    = var.project_id
  dataset_id = "nse-raw-data"
  location   = var.bigquery_location
}

module "stock_market_table" {
  source = "./modules/bigquery-table"

  project_id = var.project_id
  dataset_id = google_bigquery_dataset.stock_market.dataset_id
  table_id   = "daily_ohlcv"

  deletion_protection = true
}

module "nse_ingestion_job" {
  source = "./modules/cloud-run-job"

  job_name = "nse-stock-ingestion"

  region = var.region

  image = var.container_image

  service_account = var.cloud_run_service_account

  environment_variables = {
    GCP_PROJECT_ID = var.project_id
    BQ_DATASET     = "stock_market"
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