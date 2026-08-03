#!/usr/bin/python

# ToDo:
# - scrape the public IP and print it out as a URL for testing/verification;
# - tear down resources in an orderly fashion;
# - find a way to scale the service's task count to zero so it can be deleted via API;
#      aws ecs update-service --cluster basic-test --service basic-service --desired-count 0
# - may also be necessary:
#      aws application-autoscaling register-scalable-target \
#          --service-namespace ecs \
#          --resource-id service/<your-cluster-name>/<your-service-name> \
#          --scalable-dimension ecs:service:DesiredCount \
#          --min-capacity 0

import sys
import boto3

from json import dumps, loads

session = boto3.session.Session()
cetacean = session.client( service_name = 'ec2' )

response = cetacean.describe_subnets()

subnets = [ subnet[ 'SubnetId' ] for subnet in response[ 'Subnets' ] ]

cetacean = session.client( service_name = 'ecs' )

response = cetacean.create_cluster( clusterName = 'basic-test' )

clusterArn = response[ 'cluster' ][ 'clusterArn' ]

print( f'Created {clusterArn}' )

taskdef = {
    "containerDefinitions": [
        {
            "command": [
                "/bin/sh -c \"echo '<html><head><title>*TAP-TAP*</title></head><body><h1>Testing 1...2...3</h1></body></html>' > /usr/local/apache2/htdocs/index.html && httpd-foreground\""
            ],
            "entryPoint": [
                "sh",
		"-c"
            ],
            "essential": True,
            "image": "public.ecr.aws/docker/library/httpd:latest", 
            "name": "minimal-apache-httpd",
            "portMappings": [
                {
                    "containerPort": 80, 
                    "hostPort": 80, 
                    "protocol": "tcp"
                }
            ]
        }
    ], 
    "cpu": "256", 
    "family": "sample-fargate-httpd-container",
    "memory": "512",
    "networkMode": "awsvpc", 
    "requiresCompatibilities": [
        "FARGATE"
    ]
}

response = cetacean.register_task_definition( **loads( dumps( taskdef ) ) ) # footnote 1 #

taskDefinitionArn = response[ 'taskDefinition' ][ 'taskDefinitionArn' ]

print( f'Created {taskDefinitionArn}' )

response = cetacean.create_service(
    cluster = clusterArn,
    desiredCount = 1,
    launchType = 'FARGATE',
    networkConfiguration = {
        'awsvpcConfiguration': {
            'assignPublicIp': 'ENABLED',
            'subnets': subnets
        },
    },
    serviceName = 'basic-service',
    taskDefinition = taskDefinitionArn )

service = response[ 'service' ]
serviceArn = service[ 'serviceArn' ]

print( f'Created {serviceArn}' )

print( dumps( service, default = str ), file = sys.stderr )

# Footnote 1:
#
# Why did I do it this way, you ask?  Because I airlifted the value of
# taskdef straight from the AWS-provided tutorial
# (cf. https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started-fargate.html),
# and I didn't feel like changing all the equal-signs to colons just
# to keep it happy (cf. "TypeError: register_task_definition() only
# accepts keyword arguments.").  I want to be able to copypaste JSON
# from example pages without hand-editing it, and this allows me to do
# that.
#
# Also, note that while you only need to "register" a task definition,
# without the need to "create" it first, you *do* need to _deregister_
# it before you can delete it (or conversely, you can't delete without
# first deregistering it).  I don't know why AWS opted for this
# asymmetry in operations.  Perhaps it will become clearer to me over
# time, or perhaps it's a holdover from how they implemented it and
# they can't undo it so easily.

# rough workflow for scraping a public IP:
#
# aws ecs list-task-definitions
# aws ecs list-clusters
# aws ecs describe-clusters --clusters basic-test --include ATTACHMENTS CONFIGURATIONS SETTINGS STATISTICS TAGS
# aws ecs list-services --cluster basic-test
# aws ecs describe-services --cluster basic-test --services basic-service
# aws ecs list-tasks --cluster basic-test --service-name basic-service --query taskArns --output text > arn-task.txt
# aws ecs describe-tasks --cluster basic-test --tasks $(<arn-task.txt) --query 'tasks[].attachments[].details[?name==`networkInterfaceId`].value' --output text > eni.txt
# aws ec2 describe-network-interfaces --network-interface-ids $(<eni.txt)
# aws ec2 describe-network-interfaces --network-interface-ids $(<eni.txt) --query 'NetworkInterfaces[].Association.PublicIp' --output text > ip-public.txt
# aws ec2 describe-network-interfaces --network-interface-ids $(<eni.txt) --query 'NetworkInterfaces[].Association.PublicDnsName' --output text > dns-public.txt

# rough workflow for teardown:
#
# aws ecs update-service --cluster basic-test --service basic-service --desired-count 0
# aws ecs delete-service --cluster basic-test --service arn:aws:ecs:us-east-1:931886963281:service/basic-test/basic-service
# aws ecs delete-cluster --cluster basic-test
# aws ecs deregister-task-definition --task-definition arn:aws:ecs:us-east-1:931886963281:task-definition/sample-fargate-httpd-container:3
