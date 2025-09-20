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

# I already enabled serial for this subaccount, but I'm leaving it
# here in the comments in case I need to do it again later.
#
#response = client.get_serial_console_access_status()
#print( dumps( response, default = str ) )
#
#response = client.enable_serial_console_access()
#print( dumps( response, default = str ) )

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
    ImageId = AMI, # required
    MaxCount = 1,  # required
    MinCount = 1,  # required
    UserData = f'#!/bin/bash\n\nuseradd -g wheel -p \'{passhash}\' {username}',
)

#    SubnetId='',
#    InstanceType='t3.large',
#    ResourceType='instance,Tags=[{Key=Name,Value=soup2nuts}]',
#    MetadataOptions='HttpTokens=required,InstanceMetadataTags=enabled'

instanceId = response[ 'Instances' ][0][ 'InstanceId' ]

print( f'Created instance {instanceId}' )

console_thread = Thread( target = ConsoleToInstance, args = [ instanceId ] )

console_thread.start()
