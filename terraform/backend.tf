terraform {
  backend "gcs" {
    bucket = "nse-terrform-state"
    prefix = "nse-resource"
  }
}