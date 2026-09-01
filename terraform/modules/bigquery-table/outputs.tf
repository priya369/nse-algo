output "table_id" {
  value = google_bigquery_table.this.id
}

output "table_name" {
  value = google_bigquery_table.this.table_id
}