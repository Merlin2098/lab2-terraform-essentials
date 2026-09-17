variable "name_prefix" {
  description = "Prefix applied to all resource names in this module (e.g. \"data-platform-dev\")."
  type        = string
}

variable "account_id" {
  description = "AWS account ID, used to keep bucket names globally unique."
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
