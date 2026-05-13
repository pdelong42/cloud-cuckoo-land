#!/usr/bin/python

import sys

#from json import dumps
from crypt import crypt
from getpass import getpass
from threading import Thread
from console import ConsoleToInstance
from amiuniq import UniqueMachineImage
from instantiate import Singleton

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

# This is only necessary if you need to log-in on the console, which
# is in-turn only necessary if you can't get in via either SSM or SSH.
# SSH is unavailable if you haven't set-up any SGRs to allow for that
# access; and SSM is unavailable if you aren't using an AMI where the
# agent is already baked-in (such as Amazon Linux), and you haven't
# baked it in using ImageBuilder.
#
# But in those situations, it's still useful, so I need to stash this
# bit of code somewhere, maybe in a module that can be pulled-in as
# needed.  Note that running it as UserData will override the SSM
# agent installation that ImageBuilder implicitly bakes-in, but it can
# also be run via SSM after the image is built.
#
#username = 'somebody'
#passhash = crypt( getpass( f'Choose a password to use for the user named \'{username}\': ' ) )
#UserData = f'#!/bin/bash\n\nuseradd -g wheel -p \'{passhash}\' {username}'

#UMI = UniqueMachineImage( '137112412989',
#    architecture = 'arm64',
#    creation_date = '2026-01-22T*',
#    name = 'al2023-ami-minimal-2023.10.*-kernel-6.12-*' )
#
# When creating the instance, be sure to use an instance type that is
# ARM64, e.g.: t4g.small

#UMI = UniqueMachineImage( '309956199498',
#    architecture = 'x86_64',
#    creation_date = '2026-01-*',
#    name = 'RHEL-10.*' )

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
