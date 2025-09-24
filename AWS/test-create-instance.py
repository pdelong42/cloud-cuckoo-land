#!/usr/bin/python

import boto3

#from pprint import pp
#from json import dumps
from crypt import crypt
from getpass import getpass
from threading import Thread
from console import ConsoleToInstance

username = 'doubleu'
passhash = crypt( getpass( f'Choose a password to use for \'{username}\': ' ) )

session = boto3.session.Session()
client = session.client( service_name = 'ec2' )

response = client.describe_images(
    Filters = [
        {
            'Name' : 'name',
            'Values' : [ 'al2023-ami-2023.7.20250527.1-kernel-6.1-x86_64' ]
        }
    ],
    IncludeDeprecated = True,
    IncludeDisabled = True
)

# we only care about the first one, so picking zero-index
AMI = response[ 'Images' ][0][ 'ImageId' ]

# ToDo: pick an instance type which will support a serial console
# be careful, this actually works; and we don't want to create instances until we have more parameters defined (I think)
response = client.run_instances(
    IamInstanceProfile = {'Name':'Baseline'},
    ImageId = AMI, # required
    MaxCount = 1,  # required
    MinCount = 1,  # required
    UserData = f'#!/bin/bash\n\nuseradd -g wheel -p \'{passhash}\' {username}',
)

#    SubnetId='',
#    InstanceType='t3.large',
#    ResourceType='instance,Tags=[{Key=Name,Value=soup2nuts}]',
#    MetadataOptions='HttpTokens=required,InstanceMetadataTags=enabled'

# I should probably loop over that numerical index, rather than
# hard-coding it.  But it's not obvious how I'd do that *and* hook-up
# a console to each one (if there should be more than one).
#
instanceId = response[ 'Instances' ][0][ 'InstanceId' ]

print( f'Created instance {instanceId}' )

console_thread = Thread( target = ConsoleToInstance, args = [ instanceId ] )

console_thread.start()
