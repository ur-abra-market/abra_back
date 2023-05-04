locals {
  security_group_name = "${var.project_prefix}-security-group-${var.env}"
  database_name = "${var.project_prefix}-${var.env}"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_security_group" "rds_instance" {
  name = local.security_group_name
  description = "allow tls inbound traffic"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "tls from vpc"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "rds_instance" {
  allocated_storage = 20
  db_name = local.database_name
  engine = "postgres"
  engine_version = "14.7"
  instance_class = var.rds_instance_type
  username = local.env_vars["DATABASE_USERNAME"]
  password = local.env_vars["DATABASE_PASSWORD"]
  port = local.env_vars["DATABASE_PORT"]
  publicly_accessible = true
  vpc_security_group_ids = [aws_security_group.rds_instance.id]

  provisioner "local-exec" {
    command = "sed -i '' -e 's/DATABASE_HOSTNAME=.*/DATABASE_HOSTNAME=${aws_db_instance.rds_instance.endpoint}/' ../.env.dev"
  }
}
