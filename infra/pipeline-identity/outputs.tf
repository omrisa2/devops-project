output "AWS_ROLE_ARN" {
  value = aws_iam_role.pipeline.arn
}

output "AWS_REGION" {
  value = var.region
}
