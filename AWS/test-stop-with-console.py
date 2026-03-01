#!/usr/bin/python

import sys
import time
import boto3

# This library is in the current directory.  I don't know if that's
# what Python considers a "best pracice", but it feels gross to me.
# But I'm going to do that until I find a better way to do library
# path management in this runtime.
#
from console import ConsoleToInstance

from threading import Thread
from tagtable import Instances

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()
instanceTable = Instances()
instanceId = instanceTable.IDs[ NameTag ]
console_thread = Thread( target = ConsoleToInstance, args = [ instanceId ] )

console_thread.start()
time.sleep( 3 )

client = boto3.session.Session().client( service_name = 'ec2' )
response = client.stop_instances( InstanceIds = [ instanceId ] )

for x in response[ 'StoppingInstances' ]:

    iid = x[ 'InstanceId' ]
    prev = x[ 'PreviousState' ][ 'Name' ]
    curr = x[  'CurrentState' ][ 'Name' ]

    print( f'\nTransitioning instance {iid} from {prev} to {curr}' )
