# AWS Infrastructure Code

This directory contains all AWS infrastructure code using AWS CDK (Cloud Development Kit).

## Directory Structure

```
aws-infra/
├── network/           # VPC and network configuration
├── compute/          # EC2, ECS, Lambda, EKS configurations
├── storage/          # RDS, Redis, S3, OpenSearch configurations
├── security/         # IAM, KMS, Secrets Manager configurations
├── monitoring/       # CloudWatch, X-Ray, CloudTrail configurations
├── pipeline/         # CI/CD pipeline configuration
├── lambda/           # Lambda function code
└── cdk.json          # CDK configuration
```

## Prerequisites

- AWS CDK installed
- AWS CLI configured with appropriate credentials
- Node.js 18.x or higher
- Python 3.8 or higher

## Setup

1. Install dependencies:
```bash
npm install
```

2. Deploy infrastructure:
```bash
# Deploy specific stack
cdk deploy <stack-name>

# Deploy all stacks
cdk deploy --all
```

## Security

- All sensitive data is stored in AWS Secrets Manager
- IAM roles follow least privilege principle
- Network access is restricted using security groups
- Encryption is enabled for all data at rest and in transit

## Monitoring

- CloudWatch metrics and alarms
- X-Ray tracing
- CloudTrail logging
- Cost monitoring

## CI/CD

- CodePipeline for automated deployments
- CodeBuild for infrastructure testing
- ECR for container images
- GitHub Actions integration
