#!/usr/bin/python

# ToDo:
# - [DONE] scrape the public IP and print it out as a URL for testing/verification;
# - [DONE] tear down resources in an orderly fashion;
# - [DONE] find a way to scale the service's task count to zero so it can be deleted via API;
#      aws ecs update-service --cluster basic-cluster --service basic-service --desired-count 0
# - write some logic to 'curl ifconfig.io' and add it to the default NSG
# - start using some other NSG than the default one

import sys
import time
import boto3

from json import dumps, loads

polling_interval = 3
cluster_name = 'basic-cluster'
service_name = 'basic-service'

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

session = boto3.session.Session()
dolphin = session.client( service_name = 'ec2' )

response = dolphin.describe_subnets()

subnets = [ subnet[ 'SubnetId' ] for subnet in response[ 'Subnets' ] ]

cetacean = session.client( service_name = 'ecs' )

response = cetacean.register_task_definition( **loads( dumps( taskdef ) ) ) # footnote 1 #

taskDefinitionArn = response[ 'taskDefinition' ][ 'taskDefinitionArn' ]

print( f'Created {taskDefinitionArn}' )

response = cetacean.create_cluster( clusterName = cluster_name )

clusterArn = response[ 'cluster' ][ 'clusterArn' ]

print( f'Created {clusterArn}' )

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
    serviceName = service_name,
    taskDefinition = taskDefinitionArn )

service = response[ 'service' ]
serviceArn = service[ 'serviceArn' ]

print( f'Created {serviceArn}' )

#print( dumps( service, default = str ), file = sys.stderr )

task_count = 0

while not 0 < task_count:

    # not super elegant, but until I can think of a better idea...
    print( f'Polling task list size on a {polling_interval}s interval, until non-zero...' )
    time.sleep( polling_interval )

    response = cetacean.list_tasks( cluster = cluster_name, serviceName = service_name, launchType = 'FARGATE' )
    taskArns = response[ 'taskArns' ]
    task_count = len( taskArns )

enis = []

# again, not as elegant as I'd like, but it gets the job done...
while True:

    response = cetacean.describe_tasks( cluster = cluster_name, tasks = taskArns )

    #print( dumps( response, default = str ), file = sys.stderr )

    for task in response[ 'tasks' ]:
        for attachment in task[ 'attachments' ]:
            for detail in attachment[ 'details' ]:
                if 'networkInterfaceId' == detail[ 'name' ]:
                    enis.append( detail[ 'value' ] )

    print( f'Polling ENI list size on a {polling_interval}s interval, until non-zero...' )
    time.sleep( polling_interval )

    if 0 < len( enis ):
        break

response = dolphin.describe_network_interfaces( NetworkInterfaceIds = enis )

for nic in response[ 'NetworkInterfaces' ]:

    assoc = nic[ 'Association' ]
    ip = assoc[ 'PublicIp' ]
    dns = assoc[ 'PublicDnsName' ]

    print( f'Found DNS name and IP, run either of the following commands to test:' )
    print( f'\tcurl {dns}' )
    print( f'\tcurl {ip}' )

# rough workflow for scraping a public IP:
#
# aws ecs list-task-definitions
# aws ecs list-clusters
# aws ecs describe-clusters --clusters basic-cluster --include ATTACHMENTS CONFIGURATIONS SETTINGS STATISTICS TAGS
# aws ecs list-services --cluster basic-cluster
# aws ecs describe-services --cluster basic-cluster --services basic-service
# aws ecs list-tasks --cluster basic-cluster --service-name basic-service --query taskArns --output text > arn-task.txt
# aws ecs describe-tasks --cluster basic-cluster --tasks $(<arn-task.txt) --query 'tasks[].attachments[].details[?name==`networkInterfaceId`].value' --output text > eni.txt
# aws ec2 describe-network-interfaces --network-interface-ids $(<eni.txt)
# aws ec2 describe-network-interfaces --network-interface-ids $(<eni.txt) --query 'NetworkInterfaces[].Association.PublicIp' --output text > ip-public.txt
# aws ec2 describe-network-interfaces --network-interface-ids $(<eni.txt) --query 'NetworkInterfaces[].Association.PublicDnsName' --output text > dns-public.txt


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
