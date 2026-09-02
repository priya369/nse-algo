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

output "bigquery_table_names" {
  description = "Fully qualified BigQuery table names"
  value = {
    for table_name, table in module.bigquery_tables :
    table_name => table.table_name
  }
}