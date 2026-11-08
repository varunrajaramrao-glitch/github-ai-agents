terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "remote-state-file-test-114794477914-ap-south-1-an"
    key            = "log-analyzer-eks/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "log-analyzer-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = "ap-south-1"
}