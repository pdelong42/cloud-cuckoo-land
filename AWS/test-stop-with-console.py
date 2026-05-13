#!/usr/bin/python

import sys
import time

from threading import Thread
from instantiate import Singleton
from console import ConsoleToInstance

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()
uno = Singleton( NameTag )
console_thread = Thread( target = ConsoleToInstance, args = [ uno.ID ] )

console_thread.start()
time.sleep( 10 )
uno.stop()

# This was formerly an ugly shell one-liner:
#
# ( sleep 10 && aws ec2 stop-instances --instance-ids $(<id-instance.txt) & ) & ./test-simple-console.py $(<id-instance.txt)
