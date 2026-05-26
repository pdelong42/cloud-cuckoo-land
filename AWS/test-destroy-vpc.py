#!/usr/bin/python

import sys

from plugboard import VPC

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()
uno = VPC( NameTag )

uno.destroy()
