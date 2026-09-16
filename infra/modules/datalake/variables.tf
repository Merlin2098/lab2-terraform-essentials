variable "name_prefix" {
  description = "Prefix applied to all resource names in this module (e.g. \"data-platform-dev\")."
  type        = string
}

variable "account_id" {
  description = "AWS account ID, used to keep bucket names globally unique."
  type        = string
}

variable "aws_region" {
  description = "AWS region the module is deployed into."
  type        = string
}

variable "common_tags" {
  description = "Tags applied to every resource created by this module."
  type        = map(string)
}

variable "raw_bucket_force_destroy" {
  description = "Whether Terraform may destroy the raw bucket even when it contains objects. Keep true for dev and sandbox environments."
  type        = bool
  default     = true
}

variable "processed_bucket_force_destroy" {
  description = "Whether Terraform may destroy the processed bucket even when it contains objects. Keep true for dev and sandbox environments."
  type        = bool
  default     = true
}

variable "enable_bucket_versioning" {
  description = "Whether to enable versioning on both buckets. Defaults to false to keep dev environments cheap and easy to destroy."
  type        = bool
  default     = false
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days for the Lambda log group. Use 7 for demos and labs; set higher for production per compliance requirements."
  type        = number
  default     = 7
}

variable "lambda_runtime" {
  description = "Python runtime for the transformation Lambda."
  type        = string
  default     = "python3.13"
}

variable "lambda_pandas_layer_arn" {
  description = <<-EOT
    ARN of the AWS-managed "AWS SDK for pandas" Lambda layer (provides pandas
    and pyarrow so the function can write Parquet without a custom build).

    This ARN is region- and runtime-specific and changes over time. Verify
    the current one for your region and runtime before applying:
    AWS Console -> Lambda -> Layers -> "Add a layer" -> "AWS layers" ->
    "AWSSDKPandas-Python313" (match the runtime in `lambda_runtime`).
  EOT
  type        = string
}

variable "lambda_timeout_seconds" {
  description = "Timeout for the transformation Lambda, in seconds."
  type        = number
  default     = 60
}

variable "lambda_memory_mb" {
  description = "Memory allocated to the transformation Lambda, in MB."
  type        = number
  default     = 256
}
