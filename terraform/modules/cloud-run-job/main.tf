resource "google_cloud_run_v2_job" "this" {
  name     = var.job_name
  location = var.region

  deletion_protection = false

  template {
    template {
      service_account = var.service_account

      max_retries = var.max_retries
      timeout     = var.timeout

      containers {
        image = var.image

        dynamic "env" {
          for_each = var.environment_variables

          content {
            name  = env.key
            value = env.value
          }
        }

        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
        }
      }
    }
  }
}