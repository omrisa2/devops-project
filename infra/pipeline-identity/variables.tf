variable "region" {
  type    = string
  default = "us-west-2"
}

variable "role_name" {
  description = "The IAM role GitHub Actions assumes"
  type        = string
  default     = "devops-project-pipeline"
}

variable "github_owner" {
  description = "GitHub user that owns the repository"
  type        = string
  default     = "omrisa2"
}

variable "github_repo" {
  description = "Repository name, without the owner"
  type        = string
  default     = "devops-project"
}

# From https://api.github.com/repos/omrisa2/devops-project
variable "github_owner_id" {
  description = "Numeric ID of the owner (owner.id)"
  type        = string
  default     = "192586077"
}

variable "github_repo_id" {
  description = "Numeric ID of the repository (id)"
  type        = string
  default     = "1445397189"
}
