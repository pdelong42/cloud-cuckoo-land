#!/usr/bin/python

# ToDo:
# - [DONE] scrape the public IP and print it out as a URL for
#   testing/verification;
# - [DONE] tear down resources in an orderly fashion;
# - [DONE] find a way to scale the service's task count to zero so it
#   can be deleted via API;
#      aws ecs update-service --cluster basic-cluster --service basic-service --desired-count 0
# - [DONE] write some logic to 'curl checkip.amazonaws.com' and add it
#   to the default NSG;
# - [DONE] start using some other NSG than the default one;
# - figure-out how to block-until-ready (or less ideally,
#   poll-and-timeout) to make sure the service is listening before
#   attempting to scrape its IP and declare success or failure on that
#   basis;
# - for the non-default NSG, start by using the default VPC, with an
#   eye towards changing that later;
# - separate the creation (and deletion) of task definitions into a
#   separate workflow, because it's a bit overkill to create and
#   delete them every time we instantiate a new cluster, service, or
#   task (also suffix the name with the date, to minimize AWS
#   numbering them for us);

import sys
import time
import boto3
import requests

from json import dumps, loads
from requests.utils import is_ipv4_address, is_ipv6_address

polling_interval = 3
cluster_name = 'basic-cluster'
service_name = 'basic-service'
ipcheck_url = 'http://checkip.amazonaws.com'
#ipcheck_url = 'http://ifconfig.io/ip'

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

response = requests.get( ipcheck_url )

ip_perms = { 'FromPort': 80, 'IpProtocol': 'tcp', 'ToPort': 80 }
ip_string = response.content.decode( 'utf-8' ).strip()

if( is_ipv4_address( ip_string ) ):
    ip_perms[ 'IpRanges' ] = [ { 'CidrIp': f'{ip_string}/32' } ]
    #ip_perms[ 'IpRanges' ] = [ { 'Description': '', 'CidrIp': f'{ip_string}/32' } ]

if( is_ipv6_address( ip_string ) ):
    ip_perms[ 'Ipv6Ranges' ] = [ { 'CidrIpv6': f'{ip_string}/128' } ]
    #ip_perms[ 'Ipv6Ranges' ] = [ { 'Description': '', 'CidrIpv6': f'{ip_string}/128' } ]

if( not 'IpRanges' in ip_perms and not 'Ipv6Ranges' in ip_perms ):
    print( 'ERROR: could not find a client IP address to authorize in NSG - aborting' )
    sys.exit( 1 )

session = boto3.session.Session()
dolphin = session.client( service_name = 'ec2' )

response = dolphin.describe_subnets()

subnets = [ subnet[ 'SubnetId' ] for subnet in response[ 'Subnets' ] ]

response = dolphin.create_security_group(
    Description = 'temporary NSG for testing by rollout script',
    GroupName = 'temporary-verification' )

# this will be needed when we switch to using a non-default VPC
#    VpcId = ''

nsg_id = response[ 'GroupId' ]
nsg_arn = response[ 'SecurityGroupArn' ]

response = dolphin.authorize_security_group_ingress( GroupId = nsg_id, IpPermissions = [ ip_perms ] )

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
            'securityGroups': [ nsg_id ],
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

    url = f'http://{dns}'

    print( f'Attempting to fetch {url}...' )

    response = requests.get( url )

    print( response.content )

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
