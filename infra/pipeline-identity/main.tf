terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # The state lives in S3, not on this machine.
  # The backend block cannot use variables, so the values are written here.
  backend "s3" {
    bucket       = "omrisaban-devops-project-tfstate"
    key          = "pipeline-identity/terraform.tfstate"
    region       = "us-west-2"
    use_lockfile = true
    encrypt      = true
  }
}

provider "aws" {
  region = var.region
}

# GitHub as an identity provider: AWS accepts ID tokens GitHub signed,
# when their "aud" is sts.amazonaws.com.
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

# The role's trust policy: who may become this role.
# Only a token from GitHub, addressed to STS, for this repository's main branch.
data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # Two forms of the same identity: by name, and by name with GitHub's
    # numeric IDs (the immutable subject). A token matching either one passes.
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:${var.github_owner}/${var.github_repo}:ref:refs/heads/main",
        "repo:${var.github_owner}@${var.github_owner_id}/${var.github_repo}@${var.github_repo_id}:ref:refs/heads/main",
      ]
    }
  }
}

# The role itself: no permissions yet. The cluster configuration adds them.
resource "aws_iam_role" "pipeline" {
  name                 = var.role_name
  assume_role_policy   = data.aws_iam_policy_document.trust.json
  max_session_duration = 3600
}
