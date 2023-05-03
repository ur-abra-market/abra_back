locals {
  env_file = file("../.env.${var.env}")

  env_vars = zipmap(
    [for pair in split("\n", local.env_file) : split("=", pair)[0] if pair != "" && !startswith(pair, "#")],
    [for pair in split("\n", local.env_file) : split("=", pair)[1] if pair != "" && !startswith(pair, "#")]
  )
}

terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  access_key = local.env_vars["TF_AWS_ACCESS_KEY"]
  secret_key = local.env_vars["TF_AWS_SECRET_KEY"]
}
