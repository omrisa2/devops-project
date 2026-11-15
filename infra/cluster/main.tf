# The EKS cluster, based on the lecturer's Terraform EKS lab:
# https://github.com/YuvalShaul/k8s/tree/main/eks/terraform
# Created at the start of each work session and destroyed at its end: it costs money by the hour.

terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40" # the eks module 20.x does not support provider 6 yet
    }
  }

  # Same bucket as pipeline-identity, a different key: two separate states.
  backend "s3" {
    bucket       = "omrisaban-devops-project-tfstate"
    key          = "cluster/terraform.tfstate"
    region       = "us-west-2"
    use_lockfile = true
    encrypt      = true
  }
}

provider "aws" {
  region = var.region
}

data "aws_availability_zones" "available" {}

# 1. The network: a VPC with 2 public and 2 private subnets in 2 AZs, and one NAT gateway.
module "my_vpc_network" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, 2)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# 2. The cluster and one managed node group.
module "my_eks_cluster" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.37"

  vpc_id                   = module.my_vpc_network.vpc_id
  subnet_ids               = module.my_vpc_network.private_subnets
  control_plane_subnet_ids = module.my_vpc_network.private_subnets

  # Access entries (API), and the identity running Terraform becomes cluster admin.
  authentication_mode                      = "API_AND_CONFIG_MAP"
  enable_cluster_creator_admin_permissions = true

  cluster_endpoint_public_access = true

  cluster_addons = {
    coredns                = { most_recent = true }
    kube-proxy             = { most_recent = true }
    vpc-cni                = { most_recent = true }
    eks-pod-identity-agent = { most_recent = true }
  }

  eks_managed_node_groups = {
    default = {
      instance_types = ["t3.medium"]

      min_size     = 1
      max_size     = 3
      desired_size = var.desired_nodes

      ami_type  = "BOTTLEROCKET_x86_64"
      disk_size = 20
    }
  }

  tags = {
    Project   = "devops-project"
    Terraform = "true"
  }
}
