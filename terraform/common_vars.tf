variable "env" {
    type = string
    description = "env type"
    validation {
      condition = contains(["dev", "prod"], var.env)
      error_message = "environment must be in range ['dev', 'prod']"
    }
}

variable "aws_region" {
  type = string
}

variable "project_prefix" {
  type = string
  description = "project name"
}

variable "common_tags" {
  type = map(string)
}

variable "ec2_instance_type" {
  type = string
}

variable "rds_instance_type" {
  type = string
}
