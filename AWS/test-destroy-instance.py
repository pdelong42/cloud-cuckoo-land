#!/usr/bin/python

import boto3

from threading import Thread
from console import ConsoleToInstance
from instantiate import DestroySingleton

uno = DestroySingleton( 'soup2nuts' )

print( f'Destroyed instance {uno.ID}' )

console_thread = Thread( target = ConsoleToInstance, args = [ uno.ID ] )

console_thread.start()
