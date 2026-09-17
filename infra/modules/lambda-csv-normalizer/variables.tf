variable "name_prefix" {
  description = "Prefix applied to all resource names in this module (e.g. \"data-platform-dev\")."
  type        = string
}

variable "common_tags" {
  description = "Tags applied to every resource created by this module."
  type        = map(string)
}

variable "raw_bucket_name" {
  description = "Name of the raw bucket the Lambda is notified from."
  type        = string
}

variable "raw_bucket_arn" {
  description = "ARN of the raw bucket, used to scope the Lambda's read permission and S3 invoke permission."
  type        = string
}

variable "processed_bucket_name" {
  description = "Name of the processed bucket the Lambda writes to."
  type        = string
}

variable "processed_bucket_arn" {
  description = "ARN of the processed bucket, used to scope the Lambda's write permission."
  type        = string
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
