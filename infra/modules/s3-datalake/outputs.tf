output "raw_bucket_name" {
  description = "S3 bucket where CSV files are uploaded."
  value       = aws_s3_bucket.raw.bucket
}

output "raw_bucket_arn" {
  description = "ARN of the raw bucket."
  value       = aws_s3_bucket.raw.arn
}

output "processed_bucket_name" {
  description = "S3 bucket where normalized CSV files land."
  value       = aws_s3_bucket.processed.bucket
}

output "processed_bucket_arn" {
  description = "ARN of the processed bucket."
  value       = aws_s3_bucket.processed.arn
}
