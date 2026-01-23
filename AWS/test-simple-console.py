#!/usr/bin/python

import os
import sys

# yes, I'm bending over backwards to put stuff in 'lib' and keep using hyphens, so sue me...
component = os.path.dirname( sys.argv[0] )
sys.path.append( f'./{component}/lib/cloud-cuckoo-land/AWS' )

from console import ConsoleToInstance
from tagtable import Instances

# I'll write better arg processing later (I'm sure Python has a mod)
if 2 != len( sys.argv ):
    print( "ERROR: please provide an instance Name tag as the first (and only) arg" )
    sys.exit()

instanceTable = Instances()
instanceId = instanceTable.IDs[ sys.argv.pop() ]

ConsoleToInstance( instanceId )
