env = "dev"
aws_region = "eu-north-1"

project_prefix = "abra"

common_tags =  {
    project = "abra"
    application = "abra-app"
    env = "dev"
    comment = "managed by terraform"
}

github_connection_arn = "arn:aws:codestar-connections:eu-north-1:630574434147:connection/3f8e9d89-baff-4e89-a4ae-470e97a34f52"

ec2_instance_type = "t2.micro"
rds_instance_type = "db.t3.micro"
