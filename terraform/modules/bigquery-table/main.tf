resource "google_bigquery_table" "this" {
  project    = var.project_id
  dataset_id = var.dataset_id
  table_id   = var.table_id

  deletion_protection = var.deletion_protection

  schema = jsonencode([
    {
      name = "Symbol"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "Date"
      type = "DATE"
      mode = "REQUIRED"
    },
    {
      name = "open"
      type = "FLOAT64"
      mode = "NULLABLE"
    },
    {
      name = "high"
      type = "FLOAT64"
      mode = "NULLABLE"
    },
    {
      name = "low"
      type = "FLOAT64"
      mode = "NULLABLE"
    },
    {
      name = "close"
      type = "FLOAT64"
      mode = "NULLABLE"
    },
    {
      name = "volume"
      type = "INT64"
      mode = "NULLABLE"
    },
    {
      name = "delivery_percentage"
      type = "FLOAT64"
      mode = "NULLABLE"
    }
  ])

  time_partitioning {
    type  = "DAY"
    field = "Date"
  }

  clustering = [
    "Symbol"
  ]
}