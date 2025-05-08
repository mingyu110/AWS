## 快速开始

### 1. 部署基础设施

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 2. 部署 Lambda 函数

获取 Lambda 执行角色 ARN:

```bash
terraform output lambda_role_arn
```

使用 **AWS CLI** 部署 Lambda 函数:

```bash
cd ../lambda/scale_handler
pip install -r requirements.txt -t .
zip -r function.zip .
aws lambda create-function \
  --function-name eks-scale-handler \
  --runtime python3.9 \
  --handler scale_handler.lambda_handler \
  --role <LAMBDA_ROLE_ARN> \
  --zip-file fileb://function.zip \
  --environment "Variables={EKS_CLUSTER_NAME=eks-cost-optimization,NODEGROUP_NAME=default,MIN_SIZE=1}"
```

### 3. 更新 EventBridge 目标

使用**AWS CLI**获取 Lambda 函数 ARN:

```bash
aws lambda get-function --function-name eks-scale-handler --query 'Configuration.FunctionArn' --output text
```

更新 Terraform 配置中的 Lambda ARN 并重新应用:

```bash
cd ../../terraform
# 编辑 eventbridge.tf 文件，更新 LAMBDA_ARN_PLACEHOLDER
terraform apply
```

### 4. 功能特性

- EKS 集群自动部署
- Karpenter 动态节点管理
- Spot 实例自动调度
- 定时自动扩缩容
- Spot 实例中断监控

