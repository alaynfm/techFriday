
# RDS subnet
resource "aws_db_subnet_group" "rds_subnet_custom" {
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.project_name}-rds-subnet"
  }
}

# RDS SG
resource "aws_security_group" "rds_sg" {
  name        = "${var.project_name}-rds-sg"
  description = "RDS security group"
  vpc_id      = var.vpc_id  # Reference your VPC

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = concat(var.private_subnets, var.private_deploy_subnets)
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

#audit db
resource "aws_db_parameter_group" "custom_postgres_params" {
  family      = "postgres16"  # Asegúrate de usar la familia correcta para tu versión de PostgreSQL
  description = "Custom parameter group for ${var.project_name} PostgreSQL database"

  parameter {
    name         = "shared_preload_libraries"
    value        = "pgaudit"
    apply_method = "pending-reboot"
  }

  parameter {
    name         = "pgaudit.log"
    value        = "all"
    apply_method = "pending-reboot"
  }

  parameter {
    name         = "pgaudit.log_catalog"
    value        = "on"
    apply_method = "pending-reboot"
  }

  parameter {
    name         = "log_connections"
    value        = "on"
    apply_method = "pending-reboot"
  }

  parameter {
    name         = "log_disconnections"
    value        = "on"
    apply_method = "pending-reboot"
  }

  tags = {
    Name = "${var.project_name}-custom-postgres-params"
  }
}

# Password storage in a secret manager
resource "aws_secretsmanager_secret" "rds_password" {
  description = "RDS password for ${var.project_name} PostgreSQL database"
  tags = {
    Name = "${var.project_name}-rds-password"
  }
}

resource "random_password" "rds_password" {
  length           = 16
  special          = true
  override_special = "!#$%&()*+,-.:;<=>?[]^_{|}~"
}

resource "aws_secretsmanager_secret_version" "rds_password_version" {
  secret_id     = aws_secretsmanager_secret.rds_password.id
  secret_string = jsonencode({
    username = "testarquiCheckov"
    password = random_password.rds_password.result
  })
  depends_on = [aws_secretsmanager_secret.rds_password]
}

data "aws_secretsmanager_secret_version" "rds_password" {
  secret_id = aws_secretsmanager_secret.rds_password.id
  depends_on = [aws_secretsmanager_secret_version.rds_password_version]
}

# Free tier db
resource "aws_db_instance" "postgres" {
  identifier              = "postgresdb"
  engine                  = "postgres"
  instance_class          = "invalidType"
  allocated_storage       = 20
  db_subnet_group_name    = aws_db_subnet_group.rds_subnet_custom.name
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  username                = jsondecode(data.aws_secretsmanager_secret_version.rds_password.secret_string)["username"]
  password                = jsondecode(data.aws_secretsmanager_secret_version.rds_password.secret_string)["password"]
  skip_final_snapshot     = true
  publicly_accessible     = false
  parameter_group_name    = aws_db_parameter_group.custom_postgres_params.name
  iam_database_authentication_enabled = true  # Enable IAM authentication

  tags = {
    Name = "${var.project_name}-postgres-db"
  }
  
  depends_on = [
    aws_db_parameter_group.custom_postgres_params,
    aws_secretsmanager_secret.rds_password,
    aws_security_group.rds_sg
  ]
}

