locals {
  env_file = file("../.env.${var.env}")
  tf_env_file = file("../.env.tf.${var.env}")

  env_vars = zipmap(
        [for pair in split("\n", local.env_file) : split("=", pair)[0] if pair != "" && !startswith(pair, "#") && pair != "DATABASE_HOSTNAME"],
        [for pair in split("\n", local.env_file) : split("=", pair)[1] if pair != "" && !startswith(pair, "#")]
    )
  tf_env_vars = zipmap(
        [for pair in split("\n", local.tf_env_file) : split("=", pair)[0] if pair != "" && !startswith(pair, "#")],
        [for pair in split("\n", local.tf_env_file) : split("=", pair)[1] if pair != "" && !startswith(pair, "#")]
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
  access_key = local.tf_env_vars["AWS_ACCESS_KEY"]
  secret_key = local.tf_env_vars["AWS_SECRET_KEY"]
}
