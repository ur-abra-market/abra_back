
locals {
  application_name = "${var.project_prefix}-app-${var.env}"
  environment_name = "${var.project_prefix}-env-${var.env}"
  cert_common_name = "${var.project_prefix}-${var.env}.eu-central-1.elasticbeanstalk.com"
}

#* roles and policies
#? ec2 instance profile role
data "aws_iam_policy_document" "ec2_assume_role" {
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
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
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

#* self-signed certificate

resource "tls_private_key" "cert" {
  algorithm = "RSA"
  rsa_bits = 4096
}

resource "tls_self_signed_cert" "cert" {
  private_key_pem = tls_private_key.cert.private_key_pem

  subject {
    common_name = local.cert_common_name
    organization = "myorg"
  }
  
  validity_period_hours = 8760

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

resource "aws_acm_certificate" "cert" {
  private_key = tls_private_key.cert.private_key_pem
  certificate_body = tls_self_signed_cert.cert.cert_pem
}

#* application and environment

data "aws_elastic_beanstalk_solution_stack" "eb_solution_stack_name" {
  most_recent = true
  name_regex  = "^64bit Amazon Linux 2 (.*) running Docker"
}

resource "aws_elastic_beanstalk_application" "app" {
  name        = local.application_name
  description = "abra application for ${var.env} environment"
}

resource "aws_elastic_beanstalk_environment" "env" {
  name                = local.environment_name
  application         = aws_elastic_beanstalk_application.app.name
  solution_stack_name = data.aws_elastic_beanstalk_solution_stack.eb_solution_stack_name.name
  cname_prefix        = "abra-${var.env}"
  # depends_on = [
  #   aws_db_instance.rds_instance
  # ]

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
    value     = var.ec2_instance_type
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
    value     = aws_acm_certificate.cert.arn
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

  # setting {
  #   name      = "DATABASE_HOSTNAME"
  #   value     = aws_db_instance.rds_instance.endpoint
  #   namespace = "aws.elasticbeanstalk:application:environment"
  # }

  # dynamic "setting" {
  #   for_each = local.env_vars
  #   content {
  #     name      = setting.key
  #     value     = setting.value
  #     namespace = "aws.elasticbeanstalk:application:environment"
  #   }
  # }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "APPLICATION_URL"
    value     = local.env_vars["APPLICATION_URL"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "BACKEND_PORT"
    value     = local.env_vars["BACKEND_PORT"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "LOGGING_LEVEL"
    value     = local.env_vars["LOGGING_LEVEL"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "LOGGING_FILE_PATH"
    value     = local.env_vars["LOGGING_FILE_PATH"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "CUSTOM_LOGGING_ON"
    value     = local.env_vars["CUSTOM_LOGGING_ON"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "PYTHONPATH"
    value     = local.env_vars["PYTHONPATH"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "PYTHONUNBUFFERED"
    value     = local.env_vars["PYTHONUNBUFFERED"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "PYTHONDONTWRITEBYTECODE"
    value     = local.env_vars["PYTHONDONTWRITEBYTECODE"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DEBUG"
    value     = local.env_vars["DEBUG"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "RELOAD"
    value     = local.env_vars["RELOAD"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "HOSTNAME"
    value     = local.env_vars["HOSTNAME"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "PORT"
    value     = local.env_vars["PORT"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DOCS_URL"
    value     = local.env_vars["DOCS_URL"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "REDOC_URL"
    value     = local.env_vars["REDOC_URL"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "OPENAPI_URL"
    value     = local.env_vars["OPENAPI_URL"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DATABASE_DRIVER"
    value     = local.env_vars["DATABASE_DRIVER"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DATABASE_USERNAME"
    value     = local.env_vars["DATABASE_USERNAME"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DATABASE_PASSWORD"
    value     = local.env_vars["DATABASE_PASSWORD"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DATABASE_HOSTNAME"
    value     = local.env_vars["DATABASE_HOSTNAME"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DATABASE_PORT"
    value     = local.env_vars["DATABASE_PORT"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DATABASE_NAME"
    value     = local.env_vars["DATABASE_NAME"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ALLOW_ORIGINS"
    value     = local.env_vars["ALLOW_ORIGINS"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ALLOW_CREDENTIALS"
    value     = local.env_vars["ALLOW_CREDENTIALS"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ALLOW_METHODS"
    value     = local.env_vars["ALLOW_METHODS"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ALLOW_HEADERS"
    value     = local.env_vars["ALLOW_HEADERS"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MAIL_USERNAME"
    value     = local.env_vars["MAIL_USERNAME"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MAIL_PASSWORD"
    value     = local.env_vars["MAIL_PASSWORD"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MAIL_FROM"
    value     = local.env_vars["MAIL_FROM"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MAIL_PORT"
    value     = local.env_vars["MAIL_PORT"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MAIL_SERVER"
    value     = local.env_vars["MAIL_SERVER"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MAIL_FROM_NAME"
    value     = local.env_vars["MAIL_FROM_NAME"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MAIL_STARTTLS"
    value     = local.env_vars["MAIL_STARTTLS"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MAIL_SSL_TLS"
    value     = local.env_vars["MAIL_SSL_TLS"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "USE_CREDENTIALS"
    value     = local.env_vars["USE_CREDENTIALS"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET"
    value     = local.env_vars["AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_S3_IMAGE_USER_LOGO_BUCKET"
    value     = local.env_vars["AWS_S3_IMAGE_USER_LOGO_BUCKET"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_S3_COMPANY_IMAGES_BUCKET"
    value     = local.env_vars["AWS_S3_COMPANY_IMAGES_BUCKET"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_ACCESS_KEY_ID"
    value     = local.env_vars["AWS_ACCESS_KEY_ID"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_SECRET_ACCESS_KEY"
    value     = local.env_vars["AWS_SECRET_ACCESS_KEY"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_DEFAULT_REGION"
    value     = local.env_vars["AWS_DEFAULT_REGION"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ALGORITHM"
    value     = local.env_vars["ALGORITHM"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ACCESS_TOKEN_EXPIRATION_TIME"
    value     = local.env_vars["ACCESS_TOKEN_EXPIRATION_TIME"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "REFRESH_TOKEN_EXPIRATION_TIME"
    value     = local.env_vars["REFRESH_TOKEN_EXPIRATION_TIME"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "COOKIE_SECURE"
    value     = local.env_vars["COOKIE_SECURE"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "COOKIE_CSRF"
    value     = local.env_vars["COOKIE_CSRF"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "COOKIE_SAMESITE"
    value     = local.env_vars["COOKIE_SAMESITE"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "COOKIE_DOMAIN"
    value     = local.env_vars["COOKIE_DOMAIN"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "JWT_SECRET_KEY"
    value     = local.env_vars["JWT_SECRET_KEY"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "USER_LOGO_THUMBNAIL_X"
    value     = local.env_vars["USER_LOGO_THUMBNAIL_X"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "USER_LOGO_THUMBNAIL_Y"
    value     = local.env_vars["USER_LOGO_THUMBNAIL_Y"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ADMIN_PASSWORD"
    value     = local.env_vars["ADMIN_PASSWORD"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "SUPPLIER_EMAIL"
    value     = local.env_vars["SUPPLIER_EMAIL"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "SELLER_EMAIL"
    value     = local.env_vars["SELLER_EMAIL"]
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DEFAULT_PASSWORD"
    value     = local.env_vars["DEFAULT_PASSWORD"]
  }
}
