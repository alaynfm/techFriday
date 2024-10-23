provider "aws" {
  region = "eu-central-1"
  profile = "917559450251_ElevatedPowerUser"
}
module "vpc" {
  source             = "./vpc"
  name               = var.name
  cidr               = var.cidr
  private_subnets    = var.private_subnets
  public_subnets     = var.public_subnets
  private_deploy_subnets = var.private_deploy_subnets
  availability_zones = var.availability_zones
  environment        = var.environment
}

module "rds" {
  source                 = "./rds"
  project_name           = var.name
  private_subnet_ids     = module.vpc.private_subnet_ids
  vpc_id                 = module.vpc.id
  private_subnets        = var.private_subnets
  private_deploy_subnets = var.private_deploy_subnets

  depends_on = [module.vpc]
}
