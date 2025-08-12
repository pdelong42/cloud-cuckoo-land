#!/usr/bin/python

import sys
import boto3

# This library is in the current directory.  I don't know if that's
# what Python considers a "best pracice", but it feels gross to me.
# But I'm going to do that until I find a better way to do library
# path management in this runtime.
#
from console import ConsoleToInstance

# I'll write better arg processing later (I'm sure Python has a mod)
if 2 != len( sys.argv ):
    print( "ERROR: please provide an instance ID as the first (and only) arg" )
    sys.exit()

instanceId = sys.argv.pop()

session = boto3.session.Session()
client = session.client( service_name='ec2' )

response = client.start_instances( InstanceIds = [ instanceId ] )

for x in response[ 'StartingInstances' ]:
    print( f'Transitioning instance {x['InstanceId']} from {x['PreviousState']['Name']} to {x['CurrentState']['Name']}' )

ConsoleToInstance( instanceId )
