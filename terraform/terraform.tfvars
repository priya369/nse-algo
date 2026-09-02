project_id = "project-abf4c1be-884d-4f84-ab9"

region = "asia-south1"

bigquery_location = "asia-south1"

container_image = "asia-south1-docker.pkg.dev/project-abf4c1be-884d-4f84-ab9/nse/nse-ingestion:2bb86599046d1cf82d2fbee43795720e4878fa03"

cloud_run_service_account = "terraform-deployer@project-abf4c1be-884d-4f84-ab9.iam.gserviceaccount.com"

datasets = {

  nse_algo = {
    location = "asia-south1"
  }
  
}


tables = {

  daily_ohlcv = {

    dataset_id = "nse_algo"

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
      },
      {
        name = "high"
        type = "FLOAT64"
      },
      {
        name = "low"
        type = "FLOAT64"
      },
      {
        name = "close"
        type = "FLOAT64"
      },
      {
        name = "volume"
        type = "INT64"
      },
      {
        name = "delivery_percentage"
        type = "FLOAT64"
      }
    ])

    partition_field = "Date"
    clustering      = ["Symbol"]
  }
}