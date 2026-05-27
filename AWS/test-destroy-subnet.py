#!/usr/bin/python

import sys

from plugboard import Subnet

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()
uno = Subnet( NameTag )

uno.destroy()
