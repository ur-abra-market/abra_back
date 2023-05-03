locals {
  database_name = "${var.project_prefix}-${var.env}"
}

resource "aws_db_instance" "rds_instance" {
  allocated_storage = 20
  db_name = local.database_name
  engine = "postgres"
  engine_version = "14.7"
  instance_class = var.rds_instance_type
  username = local.env_vars["DATABASE_USERNAME"]
  password = local.env_vars["DATABASE_PASSWORD"]
}
