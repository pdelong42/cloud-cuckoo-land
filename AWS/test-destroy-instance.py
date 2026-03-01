#!/usr/bin/python

import sys
import boto3

from threading import Thread
from console import ConsoleToInstance
from instantiate import DestroySingleton

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()

uno = DestroySingleton( NameTag )

print( f'Destroyed instance {uno.ID}' )

console_thread = Thread( target = ConsoleToInstance, args = [ uno.ID ] )

console_thread.start()
