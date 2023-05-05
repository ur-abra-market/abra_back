locals {
  database_identifier = "${var.project_prefix}-database-${var.env}"
  database_identifier_prefix = "${var.project_prefix}-${var.env}"
  security_group_name = "${var.project_prefix}-security-group-${var.env}"
  subnet_group_name = "${var.project_prefix}-subnet-group-${var.env}"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true
}

resource "aws_internet_gateway" "rds_instance" {
  vpc_id = aws_vpc.main.id
}

data "aws_availability_zones" "rds_instance" {
  state = "available"
}

resource "aws_subnet" "rds_instance" {
  count = length(data.aws_availability_zones.rds_instance.names)
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.${count.index}.0/24"
  map_public_ip_on_launch = true
  availability_zone = element(data.aws_availability_zones.rds_instance.names, count.index)
}

resource "aws_db_subnet_group" "rds_instance" {
  name = local.subnet_group_name
  subnet_ids = aws_subnet.rds_instance.*.id
}

resource "aws_security_group" "rds_instance" {
  name = local.security_group_name
  description = "allow tls inbound traffic"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "tls from vpc"
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "rds_instance" {
  depends_on = [aws_internet_gateway.rds_instance]
  identifier = local.database_identifier
  allocated_storage = 20
  db_name = local.env_vars["DATABASE_NAME"]
  engine = "postgres"
  engine_version = "14.7"
  instance_class = var.rds_instance_type
  username = local.env_vars["DATABASE_USERNAME"]
  password = local.env_vars["DATABASE_PASSWORD"]
  port = local.env_vars["DATABASE_PORT"]
  publicly_accessible = true
  vpc_security_group_ids = [aws_security_group.rds_instance.id]
  db_subnet_group_name = aws_db_subnet_group.rds_instance.name
  skip_final_snapshot = true

  provisioner "local-exec" {
    command = "sed -i '' -e 's/DATABASE_HOSTNAME=.*/DATABASE_HOSTNAME=${element(split(":", aws_db_instance.rds_instance.endpoint), 0)}/' $(pwd)/../.env.${var.env}"
  }
}
