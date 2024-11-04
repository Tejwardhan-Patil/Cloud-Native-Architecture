# General Variables
variable "region" {
  description = "The region where resources will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment for deployment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "owner" {
  description = "The owner of the infrastructure"
  type        = string
  default     = "infrastructure-team"
}

# Networking and VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "List of private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnets" {
  description = "List of public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "nat_gateway_enabled" {
  description = "Enable or disable NAT gateway for private subnets"
  type        = bool
  default     = true
}

variable "internet_gateway_enabled" {
  description = "Enable or disable Internet Gateway for the VPC"
  type        = bool
  default     = true
}

# EC2 Configuration
variable "instance_type" {
  description = "Type of EC2 instance to deploy"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instances"
  type        = string
}

variable "key_pair" {
  description = "SSH key pair for EC2 access"
  type        = string
}

variable "enable_ebs_optimized" {
  description = "Enable EBS optimization for EC2 instances"
  type        = bool
  default     = true
}

variable "instance_profile" {
  description = "IAM Instance Profile for EC2 instances"
  type        = string
}

# Autoscaling Configuration
variable "min_size" {
  description = "Minimum number of instances in the autoscaling group"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of instances in the autoscaling group"
  type        = number
  default     = 5
}

variable "desired_capacity" {
  description = "Desired number of instances in the autoscaling group"
  type        = number
  default     = 2
}

variable "scaling_cooldown" {
  description = "Cooldown period before scaling in or out"
  type        = number
  default     = 300
}

variable "target_cpu_utilization" {
  description = "Target CPU utilization for scaling policies"
  type        = number
  default     = 75
}

# RDS Configuration
variable "db_instance_class" {
  description = "Instance class for the RDS database"
  type        = string
  default     = "db.t3.medium"
}

variable "db_name" {
  description = "Name of the RDS database"
  type        = string
}

variable "db_username" {
  description = "Username for the RDS database"
  type        = string
}

variable "db_password" {
  description = "Password for the RDS database"
  type        = string
  sensitive   = true
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = false
}

variable "backup_retention_period" {
  description = "Number of days to retain backups for RDS"
  type        = number
  default     = 7
}

# S3 Configuration
variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "s3_versioning" {
  description = "Enable versioning on the S3 bucket"
  type        = bool
  default     = true
}

variable "s3_lifecycle_rule_enabled" {
  description = "Enable lifecycle rule for the S3 bucket"
  type        = bool
  default     = true
}

variable "s3_lifecycle_rule_expire_days" {
  description = "Number of days before expiring S3 objects"
  type        = number
  default     = 30
}

# IAM Configuration
variable "iam_roles" {
  description = "List of IAM roles to attach to the resources"
  type        = list(string)
}

variable "enable_s3_access_logging" {
  description = "Enable access logging for S3 buckets"
  type        = bool
  default     = true
}

variable "iam_policy_name" {
  description = "Name of the IAM policy"
  type        = string
}

variable "iam_assume_role_policy" {
  description = "IAM policy document for assume role"
  type        = string
}

# CloudFront Configuration
variable "cloudfront_enabled" {
  description = "Enable CloudFront distribution for the application"
  type        = bool
  default     = true
}

variable "cloudfront_origin_id" {
  description = "Origin ID for the CloudFront distribution"
  type        = string
}

variable "cloudfront_price_class" {
  description = "Price class for CloudFront distribution"
  type        = string
  default     = "PriceClass_100"
}

# Route53 Configuration
variable "route53_zone_id" {
  description = "Route53 Zone ID for DNS management"
  type        = string
}

variable "route53_record_name" {
  description = "Record name for Route53 DNS"
  type        = string
}

variable "route53_record_type" {
  description = "Record type for Route53 DNS"
  type        = string
  default     = "A"
}

# Monitoring and Logging
variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring for EC2 instances"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Retention period for CloudWatch logs"
  type        = number
  default     = 7
}

variable "cloudwatch_alarm_threshold" {
  description = "Threshold for CloudWatch alarms"
  type        = number
  default     = 80
}

variable "cloudwatch_alarm_evaluation_periods" {
  description = "Number of periods for CloudWatch alarm evaluation"
  type        = number
  default     = 3
}

# SNS Configuration
variable "sns_topic_name" {
  description = "SNS topic for alerting"
  type        = string
}

variable "sns_subscription_emails" {
  description = "Emails to subscribe to the SNS topic"
  type        = list(string)
}

# Outputs
output "vpc_id" {
  description = "The ID of the VPC created"
  value       = aws_vpc.main.id
}

output "public_subnets" {
  description = "List of public subnets"
  value       = aws_subnet.public.*.id
}

output "private_subnets" {
  description = "List of private subnets"
  value       = aws_subnet.private.*.id
}

output "ec2_instance_ids" {
  description = "IDs of the EC2 instances"
  value       = aws_instance.web.*.id
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.main.arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.domain_name
}

output "route53_record_fqdn" {
  description = "Fully qualified domain name of the Route53 record"
  value       = aws_route53_record.main.fqdn
}