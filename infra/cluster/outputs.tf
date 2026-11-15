output "cluster_name" {
  value = module.my_eks_cluster.cluster_name
}

output "region" {
  value = var.region
}

# The command that points kubectl on this machine at the cluster.
output "kubeconfig_command" {
  value = "aws eks update-kubeconfig --name ${module.my_eks_cluster.cluster_name} --region ${var.region}"
}
