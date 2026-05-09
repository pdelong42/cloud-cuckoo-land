#!/usr/bin/python

import sys
import time
import boto3

from threading import Thread
from tagtable import Instances
from instantiate import Singleton
from console import ConsoleToInstance

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()
uno = Singleton( NameTag )

print( f'instanceId = {uno.ID}' )

console_thread = Thread( target = ConsoleToInstance, args = [ uno.ID ] )

console_thread.start()
time.sleep( 3 )

client = boto3.session.Session().client( service_name = 'ec2' )
response = client.stop_instances( InstanceIds = [ uno.ID ] )

for x in response[ 'StoppingInstances' ]:

    iid = x[ 'InstanceId' ]
    prev = x[ 'PreviousState' ][ 'Name' ]
    curr = x[  'CurrentState' ][ 'Name' ]

    print( f'\nTransitioning instance {iid} from {prev} to {curr}' )
