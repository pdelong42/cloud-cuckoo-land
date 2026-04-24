#!/usr/bin/python

import sys

#from json import dumps
from crypt import crypt
from getpass import getpass
from threading import Thread
from console import ConsoleToInstance
from amiuniq import UniqueMachineImage
from instantiate import CreateSingleton

if 2 != len( sys.argv ):
    print( "ERROR: please provide a Name tag as the first (and only) arg" )
    sys.exit()

NameTag = sys.argv.pop()

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

#UMI = UniqueMachineImage( {
#    'architecture': 'arm64',
#    'creation-date': '2026-01-22T*',
#    'name': 'al2023-ami-minimal-2023.10.*-kernel-6.12-*',
#    'owner-id': '137112412989' } )
#
# When creating the instance, be sure to use an instance type that is
# ARM64, e.g.: t4g.small

#UMI = UniqueMachineImage( {
#    'architecture': 'x86_64',
#    'creation-date': '2026-01-*',
#    'name': 'RHEL-10.*',
#    'owner-id': '309956199498'
#} )

UMI = UniqueMachineImage( { 'owner-id': '931886963281' } )

# ImageId is required
#
uno = CreateSingleton(
    NameTag,
    IamInstanceProfile = {'Name':'Baseline'},
    ImageId = UMI.ID,
    InstanceType = 't3.small' )

#    InstanceType = 't4g.small'
#    KeyName = 'framework-laptop'

print( f'Created instance {uno.ID}' )

console_thread = Thread( target = ConsoleToInstance, args = [ uno.ID ] )

console_thread.start()
