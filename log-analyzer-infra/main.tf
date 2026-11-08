terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "remote-state-file-test-114794477914-ap-south-1-an"
    key            = "log-analyzer/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "log-analyzer-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = "ap-south-1"
}

data "aws_caller_identity" "current" {}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "caller_arn" {
  value = data.aws_caller_identity.current.arn
}
variable "my_ip" {
  description = "Your public IP in CIDR form, e.g. 1.2.3.4/32"
  type        = string
}

resource "aws_security_group" "log_analyzer_sg" {
  name        = "log-analyzer-sg"
  description = "Allow SSH and app traffic from my IP only"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  ingress {
    description = "App (FastAPI)"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_iam_role" "log_analyzer_role" {
  name = "log-analyzer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_instance_profile" "log_analyzer_profile" {
  name = "log-analyzer-profile"
  role = aws_iam_role.log_analyzer_role.name
}
# Upload your public key to AWS
resource "aws_key_pair" "log_analyzer_key" {
  key_name   = "log-analyzer-key"
  public_key = file("${pathexpand("~/.ssh/log-analyzer.pub")}")
}

# Query the latest Ubuntu 22.04 AMI at plan time (don't hardcode)
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical's AWS account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "log_analyzer" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.log_analyzer_key.key_name
  vpc_security_group_ids = [aws_security_group.log_analyzer_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.log_analyzer_profile.name

        user_data = <<-EOF
    #!/bin/bash
    set -eux
    apt-get update
    apt-get install -y docker.io awscli
    systemctl enable --now docker

    # Wait until the instance's IAM role credentials are available via IMDS
    # (user_data can run before metadata credentials are ready -> "Unable to locate credentials")
    for i in $(seq 1 30); do
      if aws sts get-caller-identity --region ap-south-1 >/dev/null 2>&1; then
        echo "Credentials available."
        break
      fi
      echo "Waiting for instance credentials... ($i)"
      sleep 5
    done

    # Fetch secrets from SSM using the instance's IAM role (no keys in this script)
    GEMINI_KEY=$(aws ssm get-parameter --name "/log-analyzer/gemini-api-key" --with-decryption --region ap-south-1 --query "Parameter.Value" --output text)
    GROQ_KEY=$(aws ssm get-parameter --name "/log-analyzer/groq-api-key" --with-decryption --region ap-south-1 --query "Parameter.Value" --output text)
    SERPER_KEY=$(aws ssm get-parameter --name "/log-analyzer/serper-api-key" --with-decryption --region ap-south-1 --query "Parameter.Value" --output text)

    docker pull zxcrty/log-analyzer:slim
    docker run -d -p 8000:8000 \
      -e GEMINI_API_KEY=$GEMINI_KEY \
      -e GROQ_API_KEY=$GROQ_KEY \
      -e SERPER_API_KEY=$SERPER_KEY \
      --name la zxcrty/log-analyzer:slim
  EOF

  tags = {
    Name = "log-analyzer"
  }
}

output "instance_public_ip" {
  value = aws_instance.log_analyzer.public_ip
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/log-analyzer ubuntu@${aws_instance.log_analyzer.public_ip}"
}
resource "aws_iam_role_policy" "log_analyzer_ssm_read" {
  name = "log-analyzer-ssm-read"
  role = aws_iam_role.log_analyzer_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ReadLogAnalyzerParams"
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:ap-south-1:114794477914:parameter/log-analyzer/*"
      },
      {
        Sid    = "DecryptSecureStrings"
        Effect = "Allow"
        Action = "kms:Decrypt"
        Resource = "*"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "log_analyzer_ssm_core" {
  role       = aws_iam_role.log_analyzer_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}