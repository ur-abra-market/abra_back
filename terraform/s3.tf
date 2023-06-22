locals {
  s3_code_pipeline_artifacts_name = "${var.project_prefix}-artifacts-${var.env}"
}


resource "aws_s3_bucket" "code_pipeline" {
  bucket = local.s3_code_pipeline_artifacts_name
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "code_pipeline" {
  bucket = aws_s3_bucket.code_pipeline.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "code_pipeline" {
  bucket = aws_s3_bucket.code_pipeline.bucket
  versioning_configuration {
    status = "Enabled"
  }
}
