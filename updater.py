import boto3
import csv

# Initialize the ECS client
ecs_client = boto3.client('ecs')

# Specify your ECS cluster name
CLUSTER_NAME = 'your-cluster-name'  # Replace with your cluster name

# Path to your CSV file
CSV_FILE = 'services.csv'

# Valid Fargate CPU/memory combinations
FARGATE_COMBINATIONS = {
    "256": ["512", "1024", "2048"],
    "512": ["1024", "2048", "3072", "4096"],
    "1024": ["2048", "3072", "4096", "5120", "6144", "7168", "8192"],
    "2048": ["4096", "5120", "6144", "7168", "8192", "9216", "10240", "11264", "12288", "13312", "14336", "15360", "16384"],
    "4096": ["8192", "9216", "10240", "11264", "12288", "13312", "14336", "15360", "16384", "17408", "18432", "19456", "20480", "21504", "22528", "23552", "24576", "25600", "26624", "27648", "28672", "29696", "30720"]
}

def is_valid_fargate_combination(cpu, memory):
    cpu_str = str(cpu)
    memory_str = str(memory)
    return cpu_str in FARGATE_COMBINATIONS and memory_str in FARGATE_COMBINATIONS[cpu_str]

def update_ecs_service(service_name, cpu, memory):
    try:
        # Get the current service definition
        response = ecs_client.describe_services(
            cluster=CLUSTER_NAME,
            services=[service_name]
        )
        
        if not response['services']:
            print(f"Service {service_name} not found in cluster {CLUSTER_NAME}")
            return

        service = response['services'][0]
        task_definition_arn = service['taskDefinition']
        launch_type = service.get('launchType', 'EC2')  # Defaults to EC2 if not specified

        # Describe the current task definition
        task_def_response = ecs_client.describe_task_definition(
            taskDefinition=task_definition_arn
        )
        task_definition = task_def_response['taskDefinition']

        # Check if the service uses Fargate
        is_fargate = launch_type == 'FARGATE' or 'FARGATE' in task_definition.get('requiresCompatibilities', [])

        # Validate CPU/memory for Fargate
        if is_fargate and not is_valid_fargate_combination(cpu, memory):
            print(f"Invalid CPU={cpu}/Memory={memory} combination for Fargate in {service_name}")
            return

        # Prepare new task definition
        new_task_def = {
            'family': task_definition['family'],
            'containerDefinitions': task_definition['containerDefinitions'],
            'cpu': str(cpu),  # Task-level CPU
            'memory': str(memory),  # Task-level memory
            'networkMode': task_definition.get('networkMode', 'awsvpc'),  # Fargate requires awsvpc
            'executionRoleArn': task_definition.get('executionRoleArn'),  # Required for Fargate
            'taskRoleArn': task_definition.get('taskRoleArn'),  # Optional
            'volumes': task_definition.get('volumes', []),
        }

        # Add Fargate compatibility if needed
        if is_fargate:
            new_task_def['requiresCompatibilities'] = ['FARGATE']
            if not new_task_def['executionRoleArn']:
                print(f"Error: executionRoleArn is required for Fargate in {service_name}")
                return
            if new_task_def['networkMode'] != 'awsvpc':
                new_task_def['networkMode'] = 'awsvpc'

        # Update container definitions (remove cpu/memory if set there for Fargate)
        for container in new_task_def['containerDefinitions']:
            if is_fargate:
                container.pop('cpu', None)  # CPU must be at task level for Fargate
                container.pop('memory', None)  # Memory must be at task level for Fargate
            else:
                container['cpu'] = int(cpu)
                container['memory'] = int(memory)

        # Register the new task definition
        new_task_def_response = ecs_client.register_task_definition(**new_task_def)
        new_task_def_arn = new_task_def_response['taskDefinition']['taskDefinitionArn']

        # Update the service with the new task definition
        ecs_client.update_service(
            cluster=CLUSTER_NAME,
            service=service_name,
            taskDefinition=new_task_def_arn
        )
        print(f"Successfully updated {service_name} with CPU={cpu}, Memory={memory}")

    except Exception as e:
        print(f"Error updating {service_name}: {str(e)}")

# Read the CSV file and update services
with open(CSV_FILE, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        service_name = row['service_name']
        cpu = row['cpu']
        memory = row['memory']
        update_ecs_service(service_name, cpu, memory)
