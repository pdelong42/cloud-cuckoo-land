#!/usr/bin/python

import sys
import boto3

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

username = 'somebody'
passhash = crypt( getpass( f'Choose a password to use for the user named \'{username}\': ' ) )

UMI = UniqueMachineImage( {
    'architecture': 'arm64',
    'creation-date': '2026-01-22T*',
    'name': 'al2023-ami-minimal-2023.10.*-kernel-6.12-*',
    'owner-id': '137112412989' } )

# ImageId is required
# InstanceType needs to be one of those that support arm64
#
uno = CreateSingleton(
    NameTag,
    IamInstanceProfile = {'Name':'Baseline'},
    InstanceType = 't4g.small',
    ImageId = UMI.ID,
    UserData = f'#!/bin/bash\n\nuseradd -g wheel -p \'{passhash}\' {username}'
)

print( f'Created instance {uno.ID}' )

console_thread = Thread( target = ConsoleToInstance, args = [ uno.ID ] )

console_thread.start()
