data "aws_caller_identity" "current" {}

locals {
  name_prefix = lower(replace("${var.project_name}-${var.environment}", "_", "-"))
  common_tags = merge(
    var.tags,
    {
      Project     = var.project_name
      Environment = var.environment
      Owner       = var.owner
      ManagedBy   = "Terraform"
      CostCenter  = var.cost_center
    }
  )
}

module "datalake" {
  source = "./modules/datalake"

  name_prefix = local.name_prefix
  account_id  = data.aws_caller_identity.current.account_id
  aws_region  = var.aws_region
  common_tags = local.common_tags

  raw_bucket_force_destroy       = var.raw_bucket_force_destroy
  processed_bucket_force_destroy = var.processed_bucket_force_destroy
  enable_bucket_versioning       = var.enable_bucket_versioning
  log_retention_days             = var.log_retention_days
}
