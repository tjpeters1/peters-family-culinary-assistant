terraform {
  backend "gcs" {
    bucket = "tjpeters-experiment-sandbox-terraform-state"
    prefix = "peters-family-culinary-assistant/prod"
  }
}
