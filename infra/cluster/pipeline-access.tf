# What the pipeline's role may do with this cluster (Pipeline Identities, Part 5).
# The role itself lives in ../pipeline-identity and is never destroyed here:
# these permissions point at the cluster, so they are created and destroyed with it.

# The existing role, found by its name.
data "aws_iam_role" "pipeline" {
  name = var.pipeline_role_name
}

# In AWS: the role may read this cluster's address (aws eks update-kubeconfig).
data "aws_iam_policy_document" "describe" {
  statement {
    actions   = ["eks:DescribeCluster"]
    resources = [module.my_eks_cluster.cluster_arn]
  }
}

resource "aws_iam_role_policy" "describe" {
  name   = "describe-${var.cluster_name}"
  role   = data.aws_iam_role.pipeline.name
  policy = data.aws_iam_policy_document.describe.json
}

# In the cluster: the role may get in...
resource "aws_eks_access_entry" "pipeline" {
  cluster_name  = module.my_eks_cluster.cluster_name
  principal_arn = data.aws_iam_role.pipeline.arn
  type          = "STANDARD"
}

# ...and may edit one namespace, and nothing else.
resource "aws_eks_access_policy_association" "pipeline" {
  cluster_name  = module.my_eks_cluster.cluster_name
  principal_arn = data.aws_iam_role.pipeline.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy"

  access_scope {
    type       = "namespace"
    namespaces = [var.namespace]
  }

  depends_on = [aws_eks_access_entry.pipeline]
}
