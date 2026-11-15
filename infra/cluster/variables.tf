variable "region" {
  type    = string
  default = "us-west-2"
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "devops-project-eks"
}

variable "desired_nodes" {
  description = "How many worker nodes to run"
  type        = number
  default     = 2
}

variable "pipeline_role_name" {
  description = "The role created in ../pipeline-identity"
  type        = string
  default     = "devops-project-pipeline"
}

variable "namespace" {
  description = "The one namespace the pipeline may change"
  type        = string
  default     = "web"
}
