#!/usr/bin/python

import sys

#import os
#component = os.path.dirname( sys.argv[0] )
#sys.path.append( f'./{component}/lib/cloud-cuckoo-land/AWS' )

from console import ConsoleToInstance
from tagtable import Instances

if 2 != len( sys.argv ):
    print( "ERROR: please provide an instance Name tag as the first (and only) arg" )
    sys.exit()

instanceTable = Instances()
instanceId = instanceTable.IDs[ sys.argv.pop() ]

ConsoleToInstance( instanceId )
