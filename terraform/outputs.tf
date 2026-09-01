output "cloud_run_job_name" {
  description = "Name of the Cloud Run Job"
  value       = module.nse_ingestion_job.job_name
}

output "cloud_run_job_id" {
  description = "ID of the Cloud Run Job"
  value       = module.nse_ingestion_job.job_id
}

output "cloud_run_job_location" {
  description = "Region of the Cloud Run Job"
  value       = module.nse_ingestion_job.job_location
}

output "bigquery_table_id" {
  description = "BigQuery table ID"
  value       = module.stock_market_table.table_id
}

output "bigquery_table_name" {
  description = "BigQuery table name"
  value       = module.stock_market_table.table_name
}