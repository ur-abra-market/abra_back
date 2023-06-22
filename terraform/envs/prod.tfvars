env = "prod"
aws_region = "eu-central-1"

project_prefix = "abra"

common_tags =  {
    project = "abra"
    application = "abra-app"
    env = "prod"
    comment = "managed by terraform"
}

ec2_instance_type = "t2.micro"
rds_instance_type = "db.t3.micro"
