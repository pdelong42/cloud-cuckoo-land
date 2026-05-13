#!/usr/bin/python

import sys

from getpass import getpass
from threading import Thread
from console import ConsoleToInstance
from amiuniq import UniqueMachineImage
from instantiate import Singleton

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

# I was using my literal owner ID before I realized I could just use
# the convenience alias "self":
#
#UMI = UniqueMachineImage( '931886963281' )

NameTag = sys.argv.pop()
uno = Singleton( NameTag );
UMI = UniqueMachineImage( 'self' )

# ImageId is required.
#
# I really ought to bake IamInstanceProfile into the image, using
# ImageBuilder.  TBD.
#
uno.create(
    IamInstanceProfile = { 'Name' : 'Baseline' },
    ImageId = UMI.ID,
    InstanceType = 't3.small' )

console_thread = Thread( target = ConsoleToInstance, args = [ uno.ID ] )

console_thread.start()

# This is a good Graviton (ARM) instance type to play with:
#
#    InstanceType = 't4g.small'

# This makes for a good fallback option, in case SSM doesn't work, and
# I also didn't have the foresight to create a local login account:
#
#    KeyName = 'framework-laptop'

# other parameters to consider passing...
#    SubnetId='',
#    InstanceType='t3.large',
#    MetadataOptions='HttpTokens=required,InstanceMetadataTags=enabled'
