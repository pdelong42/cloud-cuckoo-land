#!/usr/bin/python

import sys

from plugboard import Subnet

if 3 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

# this is the threshold where I need to start using argparse
NameTag = sys.argv[1]
VpcName = sys.argv[2]

uno = Subnet( NameTag )

uno.create( VpcName = VpcName, CidrBlock = '172.31.32.0/20' )

# The CIDR block you see in this example is the same one that is used
# by create_default_subnet().  One might ask: then why not just use
# that instead?  Well, because it has one rather annoying drawback: it
# does not provide a means with which to update the tag at creation
# time.  So we could still give it a name, but it has to be a second
# call, which isn't terrible, but isn't great either.
