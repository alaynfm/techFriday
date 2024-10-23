name                   = "Ckeckov"
environment            = "test"
region                 = "eu-central-1"
availability_zones     = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
private_subnets        = ["10.0.10.0/24"]
private_deploy_subnets = ["10.0.11.0/24","10.0.12.0/24","10.0.13.0/24"]
public_subnets         = ["10.0.0.0/24"]
cidr                   = "10.0.0.0/16"
