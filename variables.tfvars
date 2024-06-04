# Remember all .tfvars files should be excluded in version control
# as there may contain sensitive data, such as password,private keys,etc.
# And this is only demo for how to write .tfvars and use it

# variables.tfvars
aws_region = "us-west-2" # Replace with your desired region
s3_bucket_lambda_functions_storage_bucket = "your-s3-bucket-name"
iam_role_ecs_task_scheduler_lambda_exec_role_arn = "your-iam-role-arn"
function_name = "ecs-task-scheduler"
iam_role_name = "ecs_task_scheduler_lambda_exec_role.name"