#!/usr/bin/python

import sys

from instantiate import Singleton
from console import ConsoleToInstance

if 2 != len( sys.argv ):
    print( "ERROR: please provide an instance Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()
uno = Singleton( NameTag )

ConsoleToInstance( uno.ID )
