output "raw_bucket_name" {
  description = "S3 bucket where CSV files are uploaded."
  value       = module.datalake.raw_bucket_name
}

output "raw_bucket_arn" {
  description = "ARN of the raw bucket."
  value       = module.datalake.raw_bucket_arn
}

output "processed_bucket_name" {
  description = "S3 bucket where transformed Parquet files land."
  value       = module.datalake.processed_bucket_name
}

output "processed_bucket_arn" {
  description = "ARN of the processed bucket."
  value       = module.datalake.processed_bucket_arn
}

output "lambda_function_name" {
  description = "Name of the CSV-to-Parquet transformation Lambda."
  value       = module.datalake.lambda_function_name
}

output "lambda_function_arn" {
  description = "ARN of the CSV-to-Parquet transformation Lambda."
  value       = module.datalake.lambda_function_arn
}

output "log_group_name" {
  description = "CloudWatch log group name for the transformation Lambda."
  value       = module.datalake.log_group_name
}

output "log_group_arn" {
  description = "CloudWatch log group ARN for the transformation Lambda."
  value       = module.datalake.log_group_arn
}
