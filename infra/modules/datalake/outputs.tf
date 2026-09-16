output "raw_bucket_name" {
  description = "S3 bucket where CSV files are uploaded."
  value       = aws_s3_bucket.raw.bucket
}

output "raw_bucket_arn" {
  description = "ARN of the raw bucket."
  value       = aws_s3_bucket.raw.arn
}

output "processed_bucket_name" {
  description = "S3 bucket where transformed Parquet files land."
  value       = aws_s3_bucket.processed.bucket
}

output "processed_bucket_arn" {
  description = "ARN of the processed bucket."
  value       = aws_s3_bucket.processed.arn
}

output "lambda_function_name" {
  description = "Name of the CSV-to-Parquet transformation Lambda."
  value       = aws_lambda_function.csv_to_parquet.function_name
}

output "lambda_function_arn" {
  description = "ARN of the CSV-to-Parquet transformation Lambda."
  value       = aws_lambda_function.csv_to_parquet.arn
}

output "log_group_name" {
  description = "CloudWatch log group name for the transformation Lambda."
  value       = aws_cloudwatch_log_group.lambda.name
}

output "log_group_arn" {
  description = "CloudWatch log group ARN for the transformation Lambda."
  value       = aws_cloudwatch_log_group.lambda.arn
}
