#!/usr/bin/python

import sys

from plugboard import VPC

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()
uno = VPC( NameTag )

uno.create( CidrBlock = '172.31.0.0/16' )

# The CIDR block you see in this example is the same one that is used
# by create_default_vpc().  One might ask: then why not just use that
# instead?  Well, because it has one rather annoying drawback: it does
# not provide a means with which to update the tag at creation time.
# So we could still give it a name, but it has to be a second call,
# which isn't terrible, but isn't great either.
