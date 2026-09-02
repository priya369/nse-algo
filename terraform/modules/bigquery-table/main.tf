resource "google_bigquery_table" "this" {
  project    = var.project_id
  dataset_id = var.dataset_id
  table_id   = var.table_id

  deletion_protection = var.deletion_protection

  schema = jsonencode(var.schema)

  dynamic "time_partitioning" {
    for_each = var.partition_field != null ? [1] : []

    content {
      type  = "DAY"
      field = var.partition_field
    }
  }

  clustering = var.clustering
}