provider "aws" {
  region = var.aws_region
}

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state-bucket-name"  # 替换为您的 S3 桶名称
    key    = "aws-cost-optimization/terraform.tfstate"
    region = "us-east-1"  # 替换为您的区域
  }
}

# 创建 AWS Config 模块
module "config" {
  source = "./modules/config"
  
  aws_region      = var.aws_region
  environment     = var.environment
  sns_topic_arn   = module.lambda.sns_topic_arn
}

# 创建 Lambda 函数模块
module "lambda" {
  source = "./modules/lambda"
  
  aws_region       = var.aws_region
  environment      = var.environment
  dingtalk_webhook = var.dingtalk_webhook
  dingtalk_secret  = var.dingtalk_secret
}

# 创建 EventBridge 模块
module "eventbridge" {
  source = "./modules/eventbridge"
  
  aws_region             = var.aws_region
  environment            = var.environment
  lambda_compliance_arn  = module.lambda.compliance_function_arn
  lambda_cost_anomaly_arn = module.lambda.cost_anomaly_function_arn
  config_topic_arn       = module.config.config_topic_arn
} 