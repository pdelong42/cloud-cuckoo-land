#!/usr/bin/python

# rough workflow for teardown:
#
# aws ecs update-service --cluster basic-cluster --service basic-service --desired-count 0
# aws ecs delete-service --cluster basic-cluster --service arn:aws:ecs:us-east-1:931886963281:service/basic-cluster/basic-service
# aws ecs delete-cluster --cluster basic-cluster
# aws ecs deregister-task-definition --task-definition arn:aws:ecs:us-east-1:931886963281:task-definition/sample-fargate-httpd-container:3

# may also be necessary:
#    aws application-autoscaling register-scalable-target \
#        --service-namespace ecs \
#        --resource-id service/<your-cluster-name>/<your-service-name> \
#        --scalable-dimension ecs:service:DesiredCount \
#        --min-capacity 0

import sys
import time
import boto3

from json import dumps, loads

polling_interval = 3
cluster_name = 'basic-cluster'
service_name = 'basic-service'

session = boto3.session.Session()

cetacean = session.client( service_name = 'ecs' )

#responses = []

response = cetacean.update_service( cluster = cluster_name, service = service_name, desiredCount = 0 )

#print( dumps( response, default = str ), file = sys.stderr )

#responses.append( response )

serviceArn = response[ 'service' ][ 'serviceArn' ]

print( f'Draining tasks from service {serviceArn}...' )

response = cetacean.delete_service( cluster = cluster_name, service = service_name )

#print( dumps( response, default = str ), file = sys.stderr )

serviceArn = response[ 'service' ][ 'serviceArn' ]
task_definition = response[ 'service' ][ 'taskDefinition' ]

print( f'Deleted service {serviceArn}' )

while True:

    # not super elegant, but until I can think of a better idea...
    print( f'Polling task list size on a {polling_interval}s interval, until zero...' )
    time.sleep( polling_interval )

    response = cetacean.list_tasks( cluster = cluster_name, serviceName = service_name, launchType = 'FARGATE' )
    taskArns = response[ 'taskArns' ]

    if not 0 < len( taskArns ):
        break

response = cetacean.delete_cluster( cluster = cluster_name )

#print( dumps( response, default = str ), file = sys.stderr )

clusterArn = response[ 'cluster' ][ 'clusterArn' ]

print( f'Deleted cluster {clusterArn}' )

response = cetacean.deregister_task_definition( taskDefinition = task_definition )

#print( dumps( response, default = str ), file = sys.stderr )

taskDefinitionArn = response[ 'taskDefinition' ][ 'taskDefinitionArn' ]

print( f'Deregistered task definition {taskDefinitionArn}' )

response = cetacean.delete_task_definitions( taskDefinitions = [ taskDefinitionArn ] )

#print( dumps( response, default = str ), file = sys.stderr )

for task in response[ 'taskDefinitions' ]:
    arn = task[ 'taskDefinitionArn' ]
    print( f'Deleted task definition {arn}' )
