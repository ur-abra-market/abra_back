
locals {
  application_name = "${var.project_prefix}-app-${var.env}"
  environment_name = "${var.project_prefix}-env-${var.env}"
}

#* roles and policies
#? ec2 instance profile role
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "ec2_instance_profile_role" {
  name               = "${var.project_prefix}_ec2_instance_profile_role_${var.env}"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "${var.project_prefix}_ec2_instance_profile_${var.env}"
  role = aws_iam_role.ec2_instance_profile_role.name
}

resource "aws_iam_role_policy_attachment" "aws_elastic_beanstalk_web_tier_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
  role       = aws_iam_role.ec2_instance_profile_role.name
}

resource "aws_iam_role_policy_attachment" "aws_elastic_beanstalk_multicontainer_docker_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
  role       = aws_iam_role.ec2_instance_profile_role.name
}

resource "aws_iam_role_policy_attachment" "aws_elastic_beanstalk_worker_tier_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"
  role       = aws_iam_role.ec2_instance_profile_role.name
}

#? elastic beanstalk service role

resource "aws_iam_role" "elastic_beanstalk_service_role" {
  name = "${var.project_prefix}_elastic_beanstalk_service_role_${var.env}"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "elasticbeanstalk.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {
          "StringEquals" : {
            "sts:ExternalId" : "elasticbeanstalk"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "aws_elastic_beanstalk_enhanced_health_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth"
  role       = aws_iam_role.elastic_beanstalk_service_role.name
}

resource "aws_iam_role_policy_attachment" "aws_elastic_beanstalk_managed_updates_customer_role_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy"
  role       = aws_iam_role.elastic_beanstalk_service_role.name
}


#* application and environment

resource "aws_elastic_beanstalk_application" "aws_elastic_beanstalk_application" {
  name        = local.application_name
  description = "abra application for ${var.env} environment"
}

resource "aws_elastic_beanstalk_environment" "aws_elastic_beanstalk_environment" {
  name                = local.environment_name
  application         = aws_elastic_beanstalk_application.aws_elastic_beanstalk_application.name
  solution_stack_name = "64bit Amazon Linux 2 v3.5.6 running Docker"
  cname_prefix        = "abra-${var.env}"

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = aws_iam_instance_profile.ec2_instance_profile.name
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "LoadBalancerType"
    value     = "application"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "ServiceRole"
    value     = aws_iam_role.elastic_beanstalk_service_role.arn
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "InstanceType"
    value     = "t2.micro"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "EnvironmentType"
    value     = "LoadBalanced"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:https"
    name      = "Protocol"
    value     = "HTTPS"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:https"
    name      = "Port"
    value     = "443"
  }

  setting {
    namespace = "aws:elbv2:listener:443"
    name      = "SSLPolicy"
    value     = "ELBSecurityPolicy-2016-08"
  }

  setting {
    namespace = "aws:elbv2:listener:443"
    name      = "ListenerEnabled"
    value     = "true"
  }

  setting {
    namespace = "aws:elbv2:listener:443"
    name      = "Protocol"
    value     = "HTTPS"
  }

  setting {
    namespace = "aws:elbv2:listener:443"
    name      = "SSLCertificateArns"
    value     = var.ssl_cert_arn
  }

  setting {
    namespace = "aws:elbv2:listener:443"
    name      = "DefaultProcess"
    value     = "default"
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MinSize"
    value     = "1"
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MaxSize"
    value     = "1"
  }

  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "SystemType"
    value     = "enhanced"
  }

  #? env vars

  dynamic "setting" {
    for_each = local.env_vars
    content {
      namespace = "aws.elasticbeanstalk:application:environment"
      name      = each.key
      value     = each.value
    }
  }
}
