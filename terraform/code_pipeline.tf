locals {
  github_connection_name = "${var.project_prefix}-connection"
  pipeline_name          = "${var.project_prefix}-pipeline-${var.env}"
  policy_name            = "${var.project_prefix}-pipeline-policy-${var.env}"
}

# assume code pipeline role
data "aws_iam_policy_document" "code_pipeline_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["codepipeline.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "code_pipeline_role" {
  name               = "test-role"
  assume_role_policy = data.aws_iam_policy_document.code_pipeline_assume_role.json
}

# code pipeline policy
data "aws_iam_policy_document" "code_pipeline_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketVersioning",
      "s3:PutObjectAcl",
      "s3:PutObject",
    ]

    resources = [
      aws_s3_bucket.code_pipeline.arn,
      "${aws_s3_bucket.code_pipeline.arn}/*"
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["codestar-connections:UseConnection"]
    resources = [local.tf_env_vars["GITHUB_CONNECTION_ARN"]]
  }

  statement {
    effect = "Allow"

    actions = [
      "codebuild:BatchGetBuilds",
      "codebuild:StartBuild",
      "codedeploy:CreateDeployment",
      "codedeploy:GetApplicationRevision",
      "codedeploy:GetApplication",
      "codedeploy:GetDeployment",
      "codedeploy:GetDeploymentConfig",
      "codedeploy:RegisterApplicationRevision",
      "elasticbeanstalk:*",
      "ec2:*",
      "elasticloadbalancing:*",
      "autoscaling:*",
      "cloudwatch:*",
      "s3:*",
      "sns:*",
      "cloudformation:*",
      "rds:*",
      "sqs:*",
      "ecs:*"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "code_pipeline_policy" {
  name   = local.policy_name
  role   = aws_iam_role.code_pipeline_role.id
  policy = data.aws_iam_policy_document.code_pipeline_policy_document.json
}

#* code pipeline instance
resource "aws_codepipeline" "mere_pipeline" {
  name     = local.pipeline_name
  role_arn = aws_iam_role.code_pipeline_role.arn

  depends_on = [
    aws_elastic_beanstalk_application.app,
    aws_elastic_beanstalk_environment.env
  ]

  artifact_store {
    location = aws_s3_bucket.code_pipeline.bucket
    type     = "S3"
  }

  stage {
    name = "Source"
    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["SourceArtifact"]

      configuration = {
        ConnectionArn    = local.tf_env_vars["GITHUB_CONNECTION_ARN"]
        FullRepositoryId = local.tf_env_vars["GITHUB_REPO"]
        BranchName       = local.tf_env_vars["GITHUB_REPO_BRANCH"]
      }
    }
  }

  stage {
    name = "Deploy"
    action {
      category = "Deploy"

      configuration = {
        ApplicationName = local.application_name
        EnvironmentName = local.environment_name
      }

      input_artifacts = ["SourceArtifact"]
      name            = "Deploy"
      namespace       = "DeployVariables"
      owner           = "AWS"
      provider        = "ElasticBeanstalk"
      region          = var.aws_region
      version         = "1"
    }
  }
}
