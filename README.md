---
​
# ECS Service CPU/Memory Updater
​
This project provides a Python script to programmatically update the CPU and memory settings of multiple Amazon ECS services in a specified cluster. The script reads service details from a CSV file and supports both EC2 and Fargate launch types, ensuring compatibility with Fargate-specific requirements.
​
## Features
- Updates CPU and memory for ECS services based on a CSV input.
- Automatically detects and adjusts for Fargate launch type constraints.
- Validates Fargate CPU/memory combinations.
- Handles task definition registration and service updates using the AWS SDK (Boto3).
​
## Prerequisites
- **Python 3.6+**: Ensure Python is installed on your system.
- **AWS Credentials**: Configured with permissions for ECS operations (see [Permissions](#permissions)).
- **Boto3**: AWS SDK for Python.
- **AWS CLI** (optional): For debugging or manual verification.
​
## Installation
1. **Clone or Download**:
   Download this script (`update_ecs_services.py`) and the accompanying files to your local machine.
​
2. **Install Dependencies**:
   Install Boto3 using pip:
   ```bash
   pip install boto3
   ```
​
3. **Configure AWS Credentials**:
   Set up your AWS credentials via:
   - AWS CLI: `aws configure`
   - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
   - IAM role (if running on an AWS instance).
​
## CSV File Format
Create a CSV file (e.g., `services.csv`) with the following columns:
- `service_name`: Name of the ECS service.
- `cpu`: Desired CPU units (e.g., `256`, `512`, `1024`).
- `memory`: Desired memory in MiB (e.g., `512`, `1024`, `2048`).
​
Example `services.csv`:
```
service_name,cpu,memory
service1,256,512
service2,512,1024
duw-prd-offensive-language,1024,2048
```
​
For Fargate services, ensure CPU/memory values match supported combinations (see [Fargate Combinations](#fargate-cpu-and-memory-combinations)).
​
## Usage
1. **Edit the Script**:
   - Open `update_ecs_services.py`.
   - Replace `your-cluster-name` with your actual ECS cluster name:
     ```python
     CLUSTER_NAME = 'your-cluster-name'
     ```
   - Optionally, update the `CSV_FILE` path if your CSV file is named differently or located elsewhere:
     ```python
     CSV_FILE = 'services.csv'
     ```
​
2. **Run the Script**:
   Execute the script from the command line:
   ```bash
   python update_ecs_services.py
   ```
​
3. **Verify Updates**:
   Check the updated services using the AWS CLI:
   ```bash
   aws ecs describe-services --cluster your-cluster-name --services <service-name>
   ```
​
## Fargate Considerations
- **Launch Type**: The script detects if a service uses Fargate and adjusts the task definition accordingly.
- **Requirements**:
  - Task-level CPU and memory settings.
  - `requiresCompatibilities` set to `["FARGATE"]`.
  - `networkMode` set to `awsvpc`.
  - Valid `executionRoleArn` in the task definition.
- **Supported Combinations**: See [Fargate CPU and Memory Combinations](#fargate-cpu-and-memory-combinations).
​
### Fargate CPU and Memory Combinations
Fargate supports specific CPU/memory pairs (in CPU units and MiB):
- **256 CPU**: 512, 1024, 2048
- **512 CPU**: 1024, 2048, 3072, 4096
- **1024 CPU**: 2048, 3072, 4096, 5120, 6144, 7168, 8192
- **2048 CPU**: 4096–16384 (increments of 1024)
- **4096 CPU**: 8192–30720 (increments of 1024)
​
The script validates these combinations automatically.
​
## Permissions
Ensure your AWS credentials have the following IAM permissions:
- `ecs:DescribeServices`
- `ecs:DescribeTaskDefinition`
- `ecs:RegisterTaskDefinition`
- `ecs:UpdateService`
​
Example IAM policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:DescribeServices",
                "ecs:DescribeTaskDefinition",
                "ecs:RegisterTaskDefinition",
                "ecs:UpdateService"
            ],
            "Resource": "*"
        }
    ]
}
```
​
## Troubleshooting
- **Error: "Task definition does not support launch_type FARGATE"**:
  - Verify the CSV CPU/memory values are valid for Fargate.
  - Ensure the task definition includes an `executionRoleArn`.
  - Check that the service uses `awsvpc` networking.
- **Service Not Found**: Confirm the service name matches exactly with what’s in the ECS cluster.
- **Permission Denied**: Check your IAM permissions or AWS credentials configuration.
- **Debugging**: Use the AWS CLI to inspect task definitions:
  ```bash
  aws ecs describe-task-definition --task-definition <task-definition-arn>
  ```
​
## Notes
- **Redeployment**: Updating a service may trigger a redeployment, potentially causing brief downtime. Test in a non-production environment first.
- **Execution Role**: If your Fargate task definition lacks an `executionRoleArn`, you’ll need to add one manually or modify the script to include it.
​
## Contributing
Feel free to submit issues or pull requests to enhance this script (e.g., adding support for more edge cases or logging).
​
## License
This project is provided as-is under the MIT License.
​
---
